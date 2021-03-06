import utils.experiment
import os
import utils.data
from models import SR
from utils import myUtils
from evaluation.Evaluation import Evaluation as Base
import dataloader
from torch import nn
import torch


class Evaluation(Base):

    def _evalIt(self, batch: utils.data.Batch):
        loss, outputs = self.experiment.model.test(batch=batch.detach(),
                                                   evalType=self.experiment.args.evalFcn)

        for input, gt, side in zip(batch.lowResRGBs(), batch.highResRGBs(), ('L', 'R')):
            outputs.addImg(name='inputSr' + side, img=input)
            outputs.addImg(name='gtSr' + side, img=gt)

        return loss, outputs.cpu()


def main():
    # Arguments
    args = utils.experiment.DefaultParser(description='evaluate SR net') \
        .outputFolder().dataPath().model().chkpoint().noCuda().seed() \
        .evalFcn().nSampleLog().dataset().loadScale().batchSize() \
        .half().resume().validSetSample().noComet().subType().mask().parse()

    # Dataset
    mask = SR.getMask(args.model)
    _, testImgLoader = dataloader.getDataLoader(dataPath=args.dataPath,
                                                dataset=args.dataset,
                                                batchSizes=args.batchSize,
                                                loadScale=(args.loadScale[0], args.loadScale[0] / 2),
                                                mode='testing' if args.subType is None else args.subType,
                                                validSetSample=args.validSetSample,
                                                mask=mask if args.mask is None else args.mask,)

    # Model
    sr = SR.getModel(args.model, cuda=args.cuda, half=args.half)

    # Test
    stage, _ = os.path.splitext(os.path.basename(__file__))
    experiment = utils.experiment.Experiment(model=sr, stage=stage, args=args)
    test = Evaluation(experiment=experiment, testImgLoader=testImgLoader)
    test()
    try:
        test.estimateFlops()
    except RuntimeError as error:
        print('Warning: ' + error.args[0])


if __name__ == '__main__':
    main()
