import utils.experiment
import torch
import torch.nn.functional as F
import torch.nn as nn
import utils.data
import utils.imProcess
from .RawPSMNet import stackhourglass as rawPSMNet
from .Stereo import Stereo
import torch.optim as optim
from apex import amp
from .RawPSMNet.stackhourglass import hourglass
from .RawPSMNet.submodule import *
from .Feature import Feature

def getRawPSMNetScale(Base):
    class RawPSMNetScale(Base):
        def __init__(self, maxDisp, dispScale, cInput=3, normalize=True):
            super().__init__(maxDisp, dispScale, cInput=cInput)
            self.multiple = 16
            self.__imagenet_stats = {'mean': [0.485, 0.456, 0.406],
                                     'std': [0.229, 0.224, 0.225]}
            self.normalize = normalize

        # input: RGB value range 0~1
        # outputs: disparity range 0~self.maxdisp * self.dispScale
        def forward(self, left, right):
            def normalize(inputRgbs):
                return (inputRgbs - torch.Tensor(self.__imagenet_stats['mean']).type_as(inputRgbs).view(1, 3, 1, 1)) \
                               / torch.Tensor(self.__imagenet_stats['std']).type_as(inputRgbs).view(1, 3, 1, 1)

            if self.normalize:
                left, right = normalize(left), normalize(right)

            if self.training:
                rawOutputs = super(RawPSMNetScale, self).forward(left, right)
            else:
                autoPad = utils.imProcess.AutoPad(left, self.multiple)

                left, right = autoPad.pad((left, right))
                rawOutputs = super(RawPSMNetScale, self).forward(left, right)
                rawOutputs = autoPad.unpad(rawOutputs)
            output = {}
            output['outputDisp'] = rawOutputs
            return output

        def load_state_dict(self, state_dict, strict=False):
            state_dict = utils.experiment.checkStateDict(
                model=self, stateDict=state_dict, strict=strict, possiblePrefix=('stereo.module.', 'module.stereoBody.'))
            super().load_state_dict(state_dict, strict=False)
    return RawPSMNetScale


class PSMNet(Stereo):
    def __init__(self, kitti, maxDisp=192, dispScale=1, cuda=True, half=False, cInput=3, normalize=True):
        super().__init__(kitti=kitti, maxDisp=maxDisp, dispScale=dispScale, cuda=cuda, half=half)
        self.cInput = cInput
        self.normalize = normalize
        self.initModel()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001, betas=(0.9, 0.999))
        if self.cuda:
            self.model.cuda()
            self.model, self.optimizer = amp.initialize(models=self.model, optimizers=self.optimizer, enabled=half)
            self.model = nn.DataParallel(self.model)

    def setLossWeights(self, lossWeights):
        if type(lossWeights) in (tuple, list):
            self.model.module.updateFeature = lossWeights[0] > 0
            super().setLossWeights(lossWeights[1])
        else:
            super().setLossWeights(lossWeights)

        print('UpdateFeature ' + ('Enabled' if self.model.module.updateFeature else 'Disabled'))

    def initModel(self):
        self.model = getRawPSMNetScale(rawPSMNet)(maxDisp=self.maxDisp, dispScale=self.dispScale, cInput=self.cInput, normalize=self.normalize)
        self.getParamNum()

    def packOutputs(self, outputs: dict, imgs: utils.imProcess.Imgs = None) -> utils.imProcess.Imgs:
        imgs = super().packOutputs(outputs, imgs)
        for key, value in outputs.items():
            if key.startswith('outputDisp'):
                if type(value) in (list, tuple):
                    value = value[2].detach()
                imgs.addImg(name=key, img=value, range=self.outMaxDisp)
        return imgs

    # input disparity maps:
    #   disparity range: 0~self.maxdisp * self.dispScale
    #   format: NCHW
    def loss(self, output: utils.imProcess.Imgs, gt: torch.Tensor, outMaxDisp=None):
        if outMaxDisp is None:
            outMaxDisp = self.outMaxDisp
        # for kitti dataset, only consider loss of none zero disparity pixels in gt
        mask = (gt > 0).detach() if self.kitti else (gt < outMaxDisp).detach()
        loss = utils.data.NameValues()
        loss['lossDisp'] = \
            0.5 * F.smooth_l1_loss(output['outputDisp'][0][mask], gt[mask], reduction='mean') \
            + 0.7 * F.smooth_l1_loss(output['outputDisp'][1][mask], gt[mask], reduction='mean') \
            + F.smooth_l1_loss(output['outputDisp'][2][mask], gt[mask], reduction='mean')
        loss['loss'] = loss['lossDisp'] * self.lossWeights

        return loss

    def train(self, batch: utils.data.Batch, progress=0):
        return self.trainBothSides(batch.oneResRGBs(), batch.oneResDisps())


class RawPSMNetBody(nn.Module):
    def __init__(self, maxdisp, dispScale=1, cInput=64):
        super().__init__()
        self.maxdisp = maxdisp
        self.dispScale = int(dispScale)
        self.outMaxDisp = self.maxdisp * self.dispScale

        self.down = nn.Sequential(nn.MaxPool2d((2, 2)),
                                  nn.Conv2d(cInput // 2, cInput // 2, 3, 1, 1),
                                  nn.MaxPool2d((2, 2)),
                                  nn.Conv2d(cInput // 2, cInput // 2, 3, 1, 1))

        self.dres0 = nn.Sequential(convbn_3d(cInput, 32, 3, 1, 1),
                                   nn.ReLU(inplace=True),
                                   convbn_3d(32, 32, 3, 1, 1),
                                   nn.ReLU(inplace=True))

        self.dres1 = nn.Sequential(convbn_3d(32, 32, 3, 1, 1),
                                   nn.ReLU(inplace=True),
                                   convbn_3d(32, 32, 3, 1, 1))

        self.dres2 = hourglass(32)

        self.dres3 = hourglass(32)

        self.dres4 = hourglass(32)

        self.classif1 = nn.Sequential(convbn_3d(32, 32, 3, 1, 1),
                                      nn.ReLU(inplace=True),
                                      nn.Conv3d(32, 1, kernel_size=3, padding=1, stride=1, bias=False))

        self.classif2 = nn.Sequential(convbn_3d(32, 32, 3, 1, 1),
                                      nn.ReLU(inplace=True),
                                      nn.Conv3d(32, 1, kernel_size=3, padding=1, stride=1, bias=False))

        self.classif3 = nn.Sequential(convbn_3d(32, 32, 3, 1, 1),
                                      nn.ReLU(inplace=True),
                                      nn.Conv3d(32, 1, kernel_size=3, padding=1, stride=1, bias=False))

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.Conv3d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.kernel_size[2] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
            elif isinstance(m, nn.BatchNorm3d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
            elif isinstance(m, nn.Linear):
                m.bias.data.zero_()

    def forward(self, left, right):

        refimg_fea = self.down(left)
        targetimg_fea = self.down(right)

        # matching
        cost = torch.zeros(refimg_fea.size()[0], refimg_fea.size()[1] * 2, self.maxdisp // 4, refimg_fea.size()[2],
                              refimg_fea.size()[3]).type_as(left).cuda()
        for i in range(self.maxdisp // 4):
            if i > 0:
                cost[:, :refimg_fea.size()[1], i, :, (i * self.dispScale):] = refimg_fea[:, :, :, (i * self.dispScale):]
                cost[:, refimg_fea.size()[1]:, i, :, (i * self.dispScale):] = targetimg_fea[:, :, :, :(-i * self.dispScale)]
            else:
                cost[:, :refimg_fea.size()[1], i, :, :] = refimg_fea
                cost[:, refimg_fea.size()[1]:, i, :, :] = targetimg_fea
        cost = cost.contiguous()

        cost0 = self.dres0(cost)
        cost0 = self.dres1(cost0) + cost0

        out1, pre1, post1 = self.dres2(cost0, None, None)
        out1 = out1 + cost0

        out2, pre2, post2 = self.dres3(out1, pre1, post1)
        out2 = out2 + cost0

        out3, pre3, post3 = self.dres4(out2, pre1, post2)
        out3 = out3 + cost0

        cost1 = self.classif1(out1)
        cost2 = self.classif2(out2) + cost1
        cost3 = self.classif3(out3) + cost2

        if self.training:
            cost1 = F.interpolate(cost1, [self.maxdisp, left.size()[2], left.size()[3]], mode='trilinear',align_corners=False)
            cost2 = F.interpolate(cost2, [self.maxdisp, left.size()[2], left.size()[3]], mode='trilinear',align_corners=False)

            cost1 = torch.squeeze(cost1, 1)
            pred1 = F.softmax(cost1, dim=1, dtype=left.dtype)
            pred1 = disparityregression(self.maxdisp)(pred1)

            cost2 = torch.squeeze(cost2, 1)
            pred2 = F.softmax(cost2, dim=1, dtype=left.dtype)
            pred2 = disparityregression(self.maxdisp)(pred2)

        cost3 = F.interpolate(cost3, [self.maxdisp, left.size()[2], left.size()[3]], mode='trilinear',align_corners=False)
        cost3 = torch.squeeze(cost3, 1)
        pred3 = F.softmax(cost3, dim=1, dtype=left.dtype)
        pred3 = disparityregression(self.maxdisp)(pred3)

        if self.training:
            return pred1.unsqueeze(1) * self.dispScale, \
                   pred2.unsqueeze(1) * self.dispScale, \
                   pred3.unsqueeze(1) * self.dispScale
        else:
            return pred3.unsqueeze(1) * self.dispScale


def getRawPSMNetBody(Base):
    class RawPSMNetScale(Base):
        def __init__(self, maxDisp, dispScale, cInput):
            super().__init__(maxDisp, dispScale, cInput)
            self.multiple = 16

        # input: Feature
        # outputs: disparity range 0~self.maxdisp * self.dispScale
        def forward(self, left, right):
            if self.training:
                rawOutputs = super(RawPSMNetScale, self).forward(left, right)
            else:
                autoPad = utils.imProcess.AutoPad(left, self.multiple)

                left, right = autoPad.pad((left, right))
                rawOutputs = super(RawPSMNetScale, self).forward(left, right)
                rawOutputs = autoPad.unpad(rawOutputs)
            output = {}
            output['outputDisp'] = rawOutputs
            return output

        def load_state_dict(self, state_dict, strict=False):
            state_dict = utils.experiment.checkStateDict(
                model=self, stateDict=state_dict, strict=strict, possiblePrefix='module.stereoBody.')
            super().load_state_dict(state_dict, strict=False)
    return RawPSMNetScale


class PSMNetBody(Stereo):
    def __init__(self, kitti, maxDisp=192, dispScale=1, cuda=True, half=False, cInput=32):
        super().__init__(kitti=kitti, maxDisp=maxDisp, dispScale=dispScale, cuda=cuda, half=half)
        self.cInput = cInput * 2
        self.initModel()
        if self.cuda:
            self.model.cuda()
            self.model = nn.DataParallel(self.model)

    def initModel(self):
        self.model = getRawPSMNetBody(RawPSMNetBody)(maxDisp=self.maxDisp, dispScale=self.dispScale, cInput=self.cInput)
        self.getParamNum()

    def packOutputs(self, outputs: dict, imgs: utils.imProcess.Imgs = None) -> utils.imProcess.Imgs:
        imgs = super().packOutputs(outputs, imgs)
        for key, value in outputs.items():
            if key.startswith('outputDisp'):
                if type(value) in (list, tuple):
                    value = value[2].detach()
                imgs.addImg(name=key, img=value, range=self.outMaxDisp)
        return imgs

    # input disparity maps:
    #   disparity range: 0~self.maxdisp * self.dispScale
    #   format: NCHW
    def loss(self, output: utils.imProcess.Imgs, gt: torch.Tensor, outMaxDisp=None):
        if outMaxDisp is None:
            outMaxDisp = self.outMaxDisp
        # for kitti dataset, only consider loss of none zero disparity pixels in gt
        mask = (gt > 0).detach() if self.kitti else (gt < outMaxDisp).detach()
        loss = utils.data.NameValues()
        loss['lossDisp'] = \
            0.5 * F.smooth_l1_loss(output['outputDisp'][0][mask], gt[mask], reduction='mean') \
            + 0.7 * F.smooth_l1_loss(output['outputDisp'][1][mask], gt[mask], reduction='mean') \
            + F.smooth_l1_loss(output['outputDisp'][2][mask], gt[mask], reduction='mean')
        loss['loss'] = loss['lossDisp'] * self.lossWeights

        return loss

class RawPSMNetFeature(nn.Module):
    def __init__(self, cInput=3):
        super().__init__()
        self.inplanes = 32
        self.firstconv = nn.Sequential(convbn(cInput, 32, 3, 2, 1, 1),
                                       nn.ReLU(inplace=True),
                                       convbn(32, 32, 3, 1, 1, 1),
                                       nn.ReLU(inplace=True),
                                       convbn(32, 32, 3, 1, 1, 1),
                                       nn.ReLU(inplace=True))

        self.layer1 = self._make_layer(BasicBlock, 32, 3, 1,1,1)
        self.layer2 = self._make_layer(BasicBlock, 64, 16, 2,1,1)
        self.layer3 = self._make_layer(BasicBlock, 128, 3, 1,1,1)
        self.layer4 = self._make_layer(BasicBlock, 128, 3, 1,1,2)

        self.branch1 = nn.Sequential(nn.AvgPool2d((64, 64), stride=(64,64)),
                                     convbn(128, 32, 1, 1, 0, 1),
                                     nn.ReLU(inplace=True))

        self.branch2 = nn.Sequential(nn.AvgPool2d((32, 32), stride=(32,32)),
                                     convbn(128, 32, 1, 1, 0, 1),
                                     nn.ReLU(inplace=True))

        self.branch3 = nn.Sequential(nn.AvgPool2d((16, 16), stride=(16,16)),
                                     convbn(128, 32, 1, 1, 0, 1),
                                     nn.ReLU(inplace=True))

        self.branch4 = nn.Sequential(nn.AvgPool2d((8, 8), stride=(8,8)),
                                     convbn(128, 32, 1, 1, 0, 1),
                                     nn.ReLU(inplace=True))

        self.lastconv = nn.Sequential(convbn(320, 128, 3, 1, 1, 1),
                                      nn.ReLU(inplace=True),
                                      nn.Conv2d(128, 32, kernel_size=1, padding=0, stride = 1, bias=False))

    def _make_layer(self, block, planes, blocks, stride, pad, dilation):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
           downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * block.expansion),)

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample, pad, dilation))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes,1,None,pad,dilation))

        return nn.Sequential(*layers)

    def forward(self, x):
        output      = self.firstconv(x)
        output      = self.layer1(output)
        output_raw  = self.layer2(output)
        output      = self.layer3(output_raw)
        output_skip = self.layer4(output)


        output_branch1 = self.branch1(output_skip)
        output_branch1 = F.interpolate(output_branch1, (output_skip.size()[2],output_skip.size()[3]),mode='bilinear',align_corners=False)

        output_branch2 = self.branch2(output_skip)
        output_branch2 = F.interpolate(output_branch2, (output_skip.size()[2],output_skip.size()[3]),mode='bilinear',align_corners=False)

        output_branch3 = self.branch3(output_skip)
        output_branch3 = F.interpolate(output_branch3, (output_skip.size()[2],output_skip.size()[3]),mode='bilinear',align_corners=False)

        output_branch4 = self.branch4(output_skip)
        output_branch4 = F.interpolate(output_branch4, (output_skip.size()[2],output_skip.size()[3]),mode='bilinear',align_corners=False)

        output_feature = torch.cat((output_raw, output_skip, output_branch4, output_branch3, output_branch2, output_branch1), 1)
        output_feature = self.lastconv(output_feature)

        output_feature = {'outputFeature': output_feature}

        return output_feature


class PSMNetFeature(Feature):
    def __init__(self, cuda=True, half=False):
        super().__init__(cuda=cuda, half=half)
        self.cOutput = 32
        self.initModel()
        if self.cuda:
            self.model.cuda()
            self.model = nn.DataParallel(self.model)

    def initModel(self):
        self.model = RawPSMNetFeature(cInput=3)
        self.getParamNum()
