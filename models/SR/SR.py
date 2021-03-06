import utils.experiment
import torch
import utils.data
import utils.imProcess
from evaluation import evalFcn
from utils import myUtils
from ..Model import Model


class SR(Model):
    def __init__(self, cuda=True, half=False):
        super().__init__(cuda=cuda, half=half)

    def predict(self, batch: utils.data.Batch, mask=(1, 1)):
        self.model.eval()

        outputs = utils.imProcess.Imgs()
        with torch.no_grad():
            for input, do, side in zip(batch.lowestResRGBs(), mask, ('L', 'R')):
                if do:
                    output = self.packOutputs(self.model(input))
                    outputs.update(imgs=output, suffix=side)

        return outputs

    def getFlops(self, inputs, show=True):
        return super().getFlops(inputs=(inputs.lowestResRGBs()[0], ))

    def testOutput(self, outputs: utils.imProcess.Imgs, gt, evalType: str):
        loss = utils.data.NameValues()
        for g, side in zip(gt, ('L', 'R')):
            output = outputs.get('outputSr' + side)
            if output is not None:
                loss[evalType + 'Sr' + side] = evalFcn.getEvalFcn(evalType)(g, output)

        return loss

    def test(self, batch: utils.data.Batch, evalType: str):
        mask = [gt is not None for gt in batch.highResRGBs()]
        outputs = self.predict(batch.lastScaleBatch(), mask)
        loss = self.testOutput(outputs=outputs, gt=batch.highResRGBs(), evalType=evalType)

        return loss, outputs

