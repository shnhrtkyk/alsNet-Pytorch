#!/bin/sh
#$ -cwd
#$ -l q_node=1
#$ -l h_rt=24:00:00

. /etc/profile.d/modules.sh



module load python/3.6.5
module load cuda/9.0.176
module load nccl/2.2.13
module load intel/19.0.0.117
module load cudnn/7.1
module load tensorflow

cd ~/alsNet/tf_ops/3d_interpolation/
sh ./tf_interpolate_compile.sh
cd ~/alsNet/tf_ops/sampling/
sh ./tf_sampling_compile.sh
cd ~/alsNet/tf_ops/grouping/
sh ./tf_grouping_compile.sh

cd ~/alsNet/


pip install --user  --upgrade pip
pip3 install --user laspy
pip3 install --user scikit-learn
pip3 install --user matplotlib


python ./alsNet/alsNetEvaluator.py --inFile "/gs/hs0/tga-ma2okalab/shino/data/test_fw_patch/*.las" --model ./logs_models/models//model_12_271/alsNet.ckpt --arch archs.arch4 --outDir ./prediction/
python ./alsNet/alsNetEvaluator2.py --inFile "/gs/hs0/tga-ma2okalab/shino/data/test_fw_patch/*.las" --model ./logs_models_fw/models/model_36_60/alsNet.ckpt --arch archs.arch4 --outDir ./prediction_fw/
python ./alsNet/alsNetEvaluator2.py --inFile "/gs/hs0/tga-ma2okalab/shino/data/test_fw_patch/*.las" --model ./logs_models_fw_fp_high/models/model_36_60/alsNet.ckpt --arch archs.arch4 --outDir ./prediction_fw_fp_high/


