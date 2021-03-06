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
kitti2015_dataset_testing=../datasets/kitti/data_scene_flow/testing/
sr_dataset=../datasets/SR

# dir setting
pretrained_dir=logs/pretrained
experiment_dir=logs/experiments
experiment_bak_dir=logs/experiments_bak

# pretrained models
pretrained_sceneflow_PSMNet=${pretrained_dir}/PSMNet_pretrained_sceneflow/PSMNet_pretrained_sceneflow.tar
pretrained_kitti2012_PSMNet=${pretrained_dir}/PSMNet_pretrained_model_KITTI2012/PSMNet_pretrained_model_KITTI2012.tar
pretrained_kitti2015_PSMNet=${pretrained_dir}/PSMNet_pretrained_model_KITTI2015/PSMNet_pretrained_model_KITTI2015.tar
pretrained_DIV2K_EDSR_baseline_x2=${pretrained_dir}/EDSR_pretrained_DIV2K/EDSR_baseline_x2.pt
pretrained_DIV2K_EDSR_x2=${pretrained_dir}/EDSR_pretrained_DIV2K/EDSR_x2.pt
pretrained_DIV2K_EDSR_x3=${pretrained_dir}/EDSR_pretrained_DIV2K/EDSR_x3.pt
pretrained_DIV2K_EDSR_x4=${pretrained_dir}/EDSR_pretrained_DIV2K/EDSR_x4.pt
pretrained_DIV2K_MDSR=${pretrained_dir}/EDSR_pretrained_DIV2K/MDSR.pt

# checkpoints: pretrain_carla_Stereo_StereoDown
pretrained_carla_PSMNetDown=${experiment_dir}/pretrain_carla_Stereo_StereoDown/Stereo_train/190410221228_StereoDown_loadScale_1.0_0.5_trainCrop_128_1024_batchSize_12_4_lossWeights_0.8_0.2_carla
pretrained_carla_PSMNetDown_largeCrop=${experiment_dir}/pretrain_carla_Stereo_StereoDown/Stereo_train/190416110029_model_StereoDown_PSMNet_loadScale_1.0_0.5_trainCrop_256_1536_batchSize_4_4_lossWeights_0.8_0.2_carla
pretrained_carla_PSMNet=${experiment_dir}/pretrain_carla_Stereo_StereoDown/Stereo_train/190416104412_model_PSMNet_loadScale_0.5_trainCrop_128_1024_batchSize_12_4_lossWeights_1_carla
pretrained_carla_GwcNetGC=${experiment_dir}/pretrain_carla_Stereo_StereoDown/Stereo_train/190521075026_model_GwcNetGC_loadScale_0.5_trainCrop_128_1024_batchSize_12_4_lossWeights_1_carla
pretrained_carla_GwcNetGCDown=${experiment_dir}/pretrain_carla_Stereo_StereoDown/Stereo_train/190521075607_model_StereoDown_GwcNetGC_loadScale_1.0_0.5_trainCrop_128_1024_batchSize_12_4_lossWeights_0.8_0.2_carla

# checkpoints: pretrain_carla_SR_SRdisp
pretrained_carla_EDSRbaseline=${experiment_dir}/compare_carla_SR_SRdisp/SR_train/190411154103_EDSR_loadScale_1_trainCrop_64_2040_batchSize_16_8_lossWeights_1_carla
pretrained_carla_EDSRbaselineDisp=${experiment_dir}/compare_carla_SR_SRdisp/SR_train/190411123543_EDSRdisp_loadScale_1_trainCrop_64_2040_batchSize_16_8_lossWeights_1_carla

# checkpoints: compare_kitti_SRStereo_Stereo
pretrained_kitti2015_PSMNet_trainSet=${experiment_dir}/compare_kitti_SRStereo_Stereo/Stereo_train/190421114842_model_PSMNet_loadScale_1_trainCrop_256_512_batchSize_12_4_lossWeights_1_kitti2015
pretrained_kitti2015_EDSRbaselinePSMNet_trainSub=${experiment_dir}/compare_kitti_SRStereo_Stereo/Stereo_train/190429080623_model_SRStereo_EDSR_PSMNet_loadScale_1.0_trainCrop_64_512_batchSize_12_4_lossWeights_-1.0_0.0_1.0_kitti2015
pretrained_kitti2015_GwcNetGC_trainSet=${experiment_dir}/compare_kitti_SRStereo_Stereo/Stereo_train/190521211229_model_GwcNetGC_loadScale_1_trainCrop_256_512_batchSize_12_4_lossWeights_1_kitti2015
pretrained_kitti2015_GwcNetGC=${experiment_dir}/compare_kitti_SRStereo_Stereo/Stereo_train/190530134811_model_GwcNetGC_loadScale_1_trainCrop_256_512_batchSize_12_4_lossWeights_1_kitti2015
pretrained_kitti2015_EDSRbaselineGwcNetGC_trainSub=${experiment_dir}/compare_kitti_SRStereo_Stereo/Stereo_train/190531045854_model_SRStereo_EDSR_GwcNetGC_loadScale_1.0_trainCrop_64_512_batchSize_12_4_lossWeights_-1.0_0.0_1.0_kitti2015/checkpoint_epoch_1200_it_00017.tar
pretrained_kitti2015_GwcNetG_trainSet=${experiment_dir}/compare_kitti_SRStereo_Stereo/Stereo_train/190617211023_model_GwcNetG_loadScale_1_trainCrop_256_512_batchSize_12_4_lossWeights_1_kitti2015
pretrained_kitti2015_GwcNetG=${experiment_dir}/compare_kitti_SRStereo_Stereo/Stereo_train/190620023441_model_GwcNetG_loadScale_1_trainCrop_256_512_batchSize_12_4_lossWeights_1_kitti2015
pretrained_kitti2015_EDSRbaselineGwcNetG_trainSub=${experiment_dir}/compare_kitti_SRStereo_Stereo/Stereo_train/190620153811_model_SRStereo_EDSR_GwcNetG_loadScale_1.0_trainCrop_64_512_batchSize_12_4_lossWeights_-1.0_0.0_1.0_kitti2015

# checkpoints: pretrain_kitti_SR
pretrained_kitti2015_EDSRbaseline=${experiment_dir}/pretrain_kitti_SR/SR_train/190421181207_model_EDSR_loadScale_1_trainCrop_64_512_batchSize_64_16_lossWeights_1_kitti2015
pretrained_kitti2015_EDSRbaseline_noArg=${experiment_dir}/pretrain_kitti_SR/SR_train/190421113622_model_EDSR_loadScale_1_trainCrop_64_512_batchSize_64_16_lossWeights_1_kitti2015
pretrained_kitti2015_EDSRbaseline_trainSub=${experiment_dir}/pretrain_kitti_SR/SR_train/190427085731_model_EDSR_loadScale_1_trainCrop_64_512_batchSize_64_16_lossWeights_1_kitti2015

# checkpoints: pretrain_sceneflow_Stereo
pretrained_sceneflow_GwcNetGC=${experiment_dir}/pretrain_sceneflow_Stereo/Stereo_train/190518203808_model_GwcNetGC_loadScale_1.0_trainCrop_256_512_batchSize_8_4_lossWeights_1_sceneflow
pretrained_sceneflow_GwcNetG=${experiment_dir}/pretrain_sceneflow_Stereo/Stereo_train/190616101518_model_GwcNetG_loadScale_1.0_trainCrop_256_512_batchSize_8_4_lossWeights_1_sceneflow
pretrained_sceneflow_EDSRfeaturePSMNetBody_bodyUpdate=${experiment_dir}/pretrain_sceneflow_Stereo/Stereo_train/190704112543_model_FeatureStereo_EDSRfeature_PSMNetBody_loadScale_1.0_trainCrop_256_512_batchSize_12_4_lossWeights_0.0_1.0_sceneflow
pretrained_sceneflow_EDSRfeaturePSMNetBody_allUpdate=${experiment_dir}/pretrain_sceneflow_Stereo/Stereo_train/190705123302_model_FeatureStereo_EDSRfeature_PSMNetBody_loadScale_1.0_trainCrop_256_512_batchSize_4_4_lossWeights_1.0_1.0_sceneflow
pretrained_sceneflow_EDSRfeaturePSMNet_stereoUpdate=${experiment_dir}/pretrain_sceneflow_Stereo/Stereo_train/190706082501_model_FeatureStereo_EDSRfeature_PSMNet_loadScale_1.0_trainCrop_256_512_batchSize_8_4_lossWeights_0.0_1.0_sceneflow
pretrained_sceneflow_EDSRfeaturePSMNet_allUpdate=${experiment_dir}/pretrain_sceneflow_Stereo/Stereo_train/190709094059_model_FeatureStereo_EDSRfeature_PSMNet_loadScale_1.0_trainCrop_256_512_batchSize_4_4_lossWeights_1.0_1.0_sceneflow
pretrained_sceneflow_PSMNet_loadPSMNetSRfeatureFixed=${experiment_dir}/pretrain_sceneflow_Stereo/Stereo_train/190809140417_model_PSMNet_loadScale_1.0_trainCrop_256_512_batchSize_12_4_lossWeights_0.0_1.0_sceneflow

# checkpoints: pretrain_div2k_SR
pretrained_DIV2K_PSMNetSR=${experiment_dir}/pretrain_div2k_SR/SR_train/190723173253_model_PSMNetSR_loadScale_1_trainCrop_96_batchSize_16_lossWeights_1_DIV2K
pretrained_DIV2K_PSMNetSRfullHalfCat=${experiment_dir}/pretrain_div2k_SR/SR_train/190726102730_model_PSMNetSRfullHalfCat_loadScale_1_trainCrop_96_batchSize_16_lossWeights_1_DIV2K
pretrained_DIV2K_PSMNetSRfullCatHalfRes=${experiment_dir}/pretrain_div2k_SR/SR_train/190729132606_model_PSMNetSRfullCatHalfRes_loadScale_1_trainCrop_512_batchSize_16_lossWeights_1_DIV2K

# checkpoints: pretrain_sceneflow_SR
pretrained_sceneflow_PSMNetSR=${experiment_dir}/pretrain_sceneflow_SR/SR_train/190806171803_model_PSMNetSR_loadScale_1_trainCrop_512_512_batchSize_16_16_lossWeights_1_sceneflow