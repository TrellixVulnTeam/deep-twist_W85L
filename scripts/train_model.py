import sys
from os.path import dirname, realpath, join
sys.path.append(dirname(dirname(realpath(__file__))))
sys.path.append(join(dirname(dirname(realpath(__file__))),
                'faster-rcnn.pytorch'))
import _init_paths

import argparse
import numpy as np
import matplotlib.pyplot as plt
import torchvision.transforms 

import torch.optim
from torch.utils.data import DataLoader
from skimage import io

import deep_twist.models.baseline
import deep_twist.models.rpn
from deep_twist.data import dataset, transforms
from deep_twist.data import utils as data_utils
from deep_twist.train import utils as train_utils 

parser = argparse.ArgumentParser(description='DeepTwist Grasp Detection Network')
parser.add_argument('--batch-size', type=int, default=1, 
                    help='batch size for training and validation') 
parser.add_argument('--device', nargs='?', type=str, default='cpu', help='device to use') 
parser.add_argument('--epochs', type=int, default=30, help='number of epochs to train') 
parser.add_argument('--lr', type=float, default=0.01, help='learning rate') 
parser.add_argument('--log-interval', type=int, default=1, help='batches between logs')
parser.add_argument('--model', nargs='?', type=str, default='deepgrasp', help='model to train') 
parser.add_argument('--val-interval', type=int, default=5, help='epochs between validations')
args = parser.parse_args()


def main():
    train_transform = torchvision.transforms.Compose([transforms.ConvertToRGD(),
                                                      transforms.SubtractImage(144),
                                                      transforms.CenterCrop(351),
                                                      transforms.RandomRotate(0, 360),
                                                      transforms.CenterCrop(321),
                                                      transforms.RandomTranslate(50),
                                                      transforms.Resize(224),
                                                      transforms.SelectRandomPos()])
    val_transform = torchvision.transforms.Compose([transforms.ConvertToRGD(),
                                                    transforms.SubtractImage(144),
                                                    transforms.CenterCrop(321),
                                                    transforms.Resize(224)]) 

    train_dataset = dataset.CornellGraspDataset('cornell/train_mini', transform=train_transform)
    val_dataset = dataset.CornellGraspDataset('cornell/val', transform=val_transform)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size,
            shuffle=False)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size,
            shuffle=False)
    
    if args.model == 'simple':
        model = deep_twist.models.baseline.Simple()
        loss = deep_twist.models.baseline.softmax_l2_loss
    if args.model == 'deepgrasp':
        model = deep_twist.models.rpn.DeepGrasp()
        loss = deep_twist.models.baseline.softmax_l2_loss  # TODO: changeeeee

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    train_utils.train_model(args, model, loss, train_loader, val_loader, optimizer)
    

if __name__ == '__main__':
    main()
