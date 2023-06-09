from torch.utils.data import DataLoader, random_split
import torchvision.datasets as dset
import torchvision.transforms as T
import torch.optim as optim

import sys

sys.path.append('./modules')
sys.path.append('./tools')
from vgg import vgg13_bn
from data_poison import data_poison

""" 数据集设置 """
num_val = 1000
batch_size = 128

poison_ratio = 0.9

transform = T.Compose([
    T.ToTensor(),
    T.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
])

original_dset = dset.CIFAR10('./data', train=True, download=True, transform=transform)
new_dset = data_poison(original_dset, poison_ratio, 0)
num_train = len(new_dset) - num_val
dset_train, dset_val = random_split(new_dset, [num_train, num_val])

# load training dataset
loader_train = DataLoader(dset_train, batch_size=batch_size, num_workers=2)

# load validation dataset
loader_val = DataLoader(dset_val, batch_size=batch_size, num_workers=2)

# load test dataset
dset_test = dset.CIFAR10('./data', train=False, download=True, transform=transform)
loader_test = DataLoader(dset_test, batch_size=batch_size, num_workers=2)

# ! model settings
model = vgg13_bn(pretrained=True, num_classes=10)

# ! optimizer
optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-3, weight_decay=1e-4)

# ! learning rate policy
lr_scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer,
                                                    mode='max',
                                                    factor=0.5,
                                                    patience=6,
                                                    min_lr=1e-5,
                                                    verbose=True)

# ! training settings
total_epochs = 20
grad_clip = None
work_dir = './work_dir/' + str(poison_ratio).replace('.', '')
save_dir = './pth_files/' + str(poison_ratio).replace('.', '') + '.pth'

# ! log settings
log_config = dict(interval=50)
