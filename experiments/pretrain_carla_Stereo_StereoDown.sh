#!/usr/bin/env bash
. ./settings.sh

# GPU settings
export CUDA_VISIBLE_DEVICES=0,1,2,3
nGPUs=$(( (${#CUDA_VISIBLE_DEVICES} + 1) / 2 ))

## StereoDown
## train PSMNetDown
#PYTHONPATH=./ python train/Stereo_train.py --model StereoDown PSMNet --outputFolder experiments/pretrain_carla_Stereo_StereoDown --dispScale 2 --dataPath $carla_dataset --dataset carla --chkpoint $pretrained_sceneflow_PSMNet --loadScale 1 0.5 --batchSize 12 $nGPUs --trainCrop 128 1024 --evalFcn l1 --epochs 10 --lr 0.001 4 0.0005 6 0.00025 8 0.000125 --lossWeights 0.75 0.25 --logEvery 50 --testEvery 2 --saveEvery 2 --half
## three times bigger cropSize
#PYTHONPATH=./ python train/Stereo_train.py --model StereoDown PSMNet --outputFolder experiments/pretrain_carla_Stereo_StereoDown --dispScale 2 --dataPath $carla_dataset --dataset carla --chkpoint $pretrained_sceneflow_PSMNet --loadScale 1 0.5 --batchSize 4 $nGPUs --trainCrop 256 1536 --evalFcn l1 --epochs 10 --lr 0.001 4 0.0005 6 0.00025 8 0.000125 --lossWeights 0.75 0.25 --logEvery 50 --testEvery 2 --saveEvery 2 --half
# train GwcNetGCDown
#PYTHONPATH=./ python train/Stereo_train.py --model StereoDown GwcNetGC --outputFolder experiments/pretrain_carla_Stereo_StereoDown --dispScale 2 --dataPath $carla_dataset --dataset carla --chkpoint $pretrained_sceneflow_GwcNetGC --loadScale 1 0.5 --batchSize 12 $nGPUs --trainCrop 128 1024 --evalFcn l1 --epochs 10 --lr 0.001 4 0.0005 6 0.00025 8 0.000125 --lossWeights 0.75 0.25 --logEvery 50 --testEvery 2 --saveEvery 2 --half


## Stereo
## train PSMNet
#PYTHONPATH=./ python train/Stereo_train.py --model PSMNet --outputFolder experiments/pretrain_carla_Stereo_StereoDown --dispScale 1 --dataPath $carla_dataset --dataset carla --chkpoint $pretrained_sceneflow_PSMNet --loadScale 0.5 --batchSize 12 $nGPUs --trainCrop 128 1024 --evalFcn l1 --epochs 10 --lr 0.001 4 0.0005 6 0.00025 8 0.000125 --logEvery 50 --testEvery 2 --saveEvery 2 --half
# train GwcNetGC
#PYTHONPATH=./ python train/Stereo_train.py --model GwcNetGC --outputFolder experiments/pretrain_carla_Stereo_StereoDown --dispScale 1 --dataPath $carla_dataset --dataset carla --chkpoint $pretrained_sceneflow_GwcNetGC --loadScale 0.5 --batchSize 12 $nGPUs --trainCrop 128 1024 --evalFcn l1 --epochs 10 --lr 0.001 4 0.0005 6 0.00025 8 0.000125 --logEvery 50 --testEvery 2 --saveEvery 2 --half

