#!/usr/bin/env bash

cd ../

# datasets
carla_dataset=../datasets/carla/carla_sr_lowquality/
carla_dataset_moduletest=../datasets/carla/carla_sr_lowquality_moduletest
carla_dataset_overfit=../datasets/carla/carla_sr_lowquality_overfit
sceneflow_dataset=../datasets/sceneflow/
kitti2015_dataset=../datasets/kitti/data_scene_flow/training/
kitti2015_sr_dataset=../datasets/kitti/data_scene_flow_sr/training/
kitti2015_dense_dataset=../datasets/kitti/data_scene_flow_dense/training/
kitti2012_dataset=../datasets/kitti/data_stereo_flow/training/

# dir setting
pretrained_dir=logs/pretrained
experiment_dir=logs/experiments
experiment_bak_dir=logs/experiments_bak

# pretrained models
pretrained_sceneflow_PSMNet=${pretrained_dir}/PSMNet_pretrained_sceneflow/PSMNet_pretrained_sceneflow.tar
pretrained_kitti2012_PSMNet=${pretrained_dir}/PSMNet_pretrained_model_KITTI2012/PSMNet_pretrained_model_KITTI2012.tar
pretrained_kitti2015_PSMNet=${pretrained_dir}/PSMNet_pretrained_model_KITTI2015/PSMNet_pretrained_model_KITTI2015.tar
pretrained_EDSR_DIV2K=${pretrained_dir}/EDSR_pretrained_DIV2K/EDSR_baseline_x2.pt

# checkpoints: pretrain_carla_Stereo_StereoDown
pretrained_carla_PSMNetDown=${experiment_dir}/pretrain_carla_Stereo_StereoDown/Stereo_train/190410221228_StereoDown_loadScale_1.0_0.5_trainCrop_128_1024_batchSize_12_4_lossWeights_0.8_0.2_carla
pretrained_carla_PSMNetDown_largeCrop=${experiment_dir}/pretrain_carla_Stereo_StereoDown/Stereo_train/190416110029_model_StereoDown_PSMNet_loadScale_1.0_0.5_trainCrop_256_1536_batchSize_4_4_lossWeights_0.8_0.2_carla
pretrained_carla_PSMNet=${experiment_dir}/pretrain_carla_Stereo_StereoDown/Stereo_train/190416104412_model_PSMNet_loadScale_0.5_trainCrop_128_1024_batchSize_12_4_lossWeights_1_carla

# checkpoints: pretrain_carla_SR_SRdisp
pretrained_carla_EDSRbaseline=${experiment_dir}/compare_carla_SR_SRdisp/SR_train/190411154103_EDSR_loadScale_1_trainCrop_64_2040_batchSize_16_8_lossWeights_1_carla
pretrained_carla_EDSRbaselineDisp=${experiment_dir}/compare_carla_SR_SRdisp/SR_train/190411123543_EDSRdisp_loadScale_1_trainCrop_64_2040_batchSize_16_8_lossWeights_1_carla

# checkpoints: compare_kitti_SRStereo_Stereo
pretrained_kitti2015_PSMNet_trainSet=${experiment_dir}/compare_kitti_SRStereo_Stereo/Stereo_train/190421114842_model_PSMNet_loadScale_1_trainCrop_256_512_batchSize_12_4_lossWeights_1_kitti2015

# checkpoints: pretrain_kitti_SR
pretrained_kitti2015_EDSRbaseline=${experiment_dir}/pretrain_kitti_SR/SR_train/190421181207_model_EDSR_loadScale_1_trainCrop_64_512_batchSize_64_16_lossWeights_1_kitti2015
pretrained_kitti2015_EDSRbaseline_noArg=${experiment_dir}/pretrain_kitti_SR/SR_train/190421113622_model_EDSR_loadScale_1_trainCrop_64_512_batchSize_64_16_lossWeights_1_kitti2015
