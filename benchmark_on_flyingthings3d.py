#!/usr/bin/env python
# Copyrights. All rights reserved.
# ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland,
# Space Center (eSpace), 2018
# See the LICENSE.TXT file for more details.
"""Script performs benchmarking on flyingthings3D.

Benchmarking in performed with maximum disparity of 191 on
960 x 540 full-size images.

Depending on the parameters, the benchmarking can be performed
using "psm" or "crl" protocol. "psm" protocol is described in
"Pyramid stereo matching network" by Jia-Ren Chang et al.
"crl" protocol is described in "Cascade Residual Learning:
A Two-stage Convolutional Neural Network for Stereo Matching"
by Jiahao Pang. According to the "psm" examples where more than
25% of pixels have disparity larger than 300 pixels are excluded
from the evaluation. According to the "crl" protocol it pixels with
ground truth disparities larger than 192 pixels are masked out
and excluded from the evaluation.

Optionally, the user can pass to the script:
"dataset_folder" with flyinghtings3d dataset;
"experiment_folder" where experiment results are be saved;
"checkpoint_file" with checkpoint that will be loaded
                  to perform evaluation training.
"is_psm_protocol" if this flag is set than evaluation is performed
                  according to "psm" protocol, otherwise "crl" protocol
                  is used.

Example call:

./benchmark_on_flyingthings3d.py \
    --experiment_folder experiments/flyingthings3d \
    --dataset_folder datasets/flyingthings3d \
    --checkpoint_file experiments/flyingthings3d/003_checkpoint.bin \
    --is_psm_protocol
"""

import os
import click

from torch.utils import data

from practical_deep_stereo import flyingthings3d_dataset
from practical_deep_stereo import pds_network
from practical_deep_stereo import trainer


def _initialize_parameters(dataset_folder, experiment_folder, is_psm_protocol):
    test_set = \
        flyingthings3d_dataset.FlyingThings3D.benchmark_dataset(
                dataset_folder, is_psm_protocol)
    test_set_loader = data.DataLoader(
        test_set, batch_size=1, shuffle=False, num_workers=1, pin_memory=True)
    network = pds_network.PdsNetwork().cuda()
    network.set_maximum_disparity(191)
    return {
        'network': network,
        'test_set_loader': test_set_loader,
        'experiment_folder': experiment_folder
    }


@click.command()
@click.option(
    '--dataset_folder',
    default='datasets/flyingthings3d',
    type=click.Path(exists=True))
@click.option(
    '--experiment_folder',
    default='experiments/flyingthings3d_benchmarking',
    type=click.Path(exists=False))
@click.option(
    '--checkpoint_file',
    default='experiments/flyingthings3d/008_checkpoint.bin',
    type=click.Path(exists=True))
@click.option('--is_psm_protocol', is_flag=True)
def benchmark_on_flyingthings3d(dataset_folder, experiment_folder,
                                checkpoint_file, is_psm_protocol):
    if not os.path.isdir(experiment_folder):
        os.mkdir(experiment_folder)
    dataset_folder = os.path.abspath(dataset_folder)
    experiment_folder = os.path.abspath(experiment_folder)
    checkpoint_file = os.path.abspath(checkpoint_file)
    pds_trainer = trainer.PdsTrainer(
        _initialize_parameters(dataset_folder, experiment_folder,
                               is_psm_protocol))
    pds_trainer.load_checkpoint(checkpoint_file, load_only_network=True)
    pds_trainer.test()


if __name__ == '__main__':
    benchmark_on_flyingthings3d()