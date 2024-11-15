"""
Scipt for subsampling spatial and label dimensions of Cityscapes segmentations.
"""

from PIL import Image
import numpy as np
import torch

class Scale(object):
    def __init__(self, scaling, interpolation=Image.NEAREST):
        self.scaling = scaling
        self.interpolation = interpolation

    def __call__(self, img):
        scaled_size = [int(self.scaling*x) for x in img.size]
        return img.resize(scaled_size, self.interpolation)

class LabelMaskToTensor(object):
    """
    Transform the label mask png files to label tensors (type long).
    Helpful source for this transform was
    https://github.com/zijundeng/pytorch-semantic-segmentation/blob/master/utils/transforms.py
    """
    def __call__(self, mask):
        return torch.from_numpy(np.array(mask, dtype=np.int32)).long()

if __name__ == '__main__':
    import argparse
    import os.path
    from tqdm import tqdm
    from torchvision.transforms import Compose # type: ignore
    from torchvision.datasets import Cityscapes # type: ignore

    parser = argparse.ArgumentParser(
        prog='DownsampleCityscapesLabelings',
        description='Downsample spatial and channel dimensions of cityscapes segmentations.')
    parser.add_argument("root_path", type=str, help="Location of original Cityscapes data.")
    parser.add_argument("scale", type=int, help="Downsample spatial dimensions by this factor.")
    parser.add_argument("split", type=str, choices=["train", "val", "test"])
    args = parser.parse_args()

    assert args.scale > 0

    full_dims = [1024, 2048]
    scale_factor = 1.0/args.scale
    coarse_dims = [int(d*scale_factor) for d in full_dims]
    target_transform = Compose([
        Scale(scale_factor),
        LabelMaskToTensor()
    ])
    ds = Cityscapes(args.root_path, split=args.split, mode="fine", target_type="semantic",
        target_transform=target_transform)
    (_, x) = ds[1]

    tensor_dataset = torch.empty(len(ds), *coarse_dims, dtype=torch.long)
    for i in tqdm(range(len(ds))):
        (_, x) = ds[i]

        # reduce class set to categories (c=8)
        y = torch.empty_like(x)
        for c in ds.classes:
            y[x == c.id] = c.category_id

        tensor_dataset[i,:,:] = y

    directory = "./cityscapes"
    if not os.path.isdir(directory):
        os.makedirs(directory, exist_ok=True)
    savepath = os.path.join(directory, f"cityscapes_{args.split}_{scale_factor}.pt")
    print("saving to", savepath)
    torch.save(tensor_dataset, savepath)

    """
    The official documentation at
    https://pytorch.org/vision/stable/_modules/torchvision/datasets/cityscapes.html
    gives the following information about image segments

    CityscapesClass = namedtuple(
        "CityscapesClass",
        ["name", "id", "train_id", "category", "category_id", "has_instances", "ignore_in_eval", "color"],
    )

    classes = [
        CityscapesClass("unlabeled", 0, 255, "void", 0, False, True, (0, 0, 0)),
        CityscapesClass("ego vehicle", 1, 255, "void", 0, False, True, (0, 0, 0)),
        CityscapesClass("rectification border", 2, 255, "void", 0, False, True, (0, 0, 0)),
        CityscapesClass("out of roi", 3, 255, "void", 0, False, True, (0, 0, 0)),
        CityscapesClass("static", 4, 255, "void", 0, False, True, (0, 0, 0)),
        CityscapesClass("dynamic", 5, 255, "void", 0, False, True, (111, 74, 0)),
        CityscapesClass("ground", 6, 255, "void", 0, False, True, (81, 0, 81)),
        CityscapesClass("road", 7, 0, "flat", 1, False, False, (128, 64, 128)),
        CityscapesClass("sidewalk", 8, 1, "flat", 1, False, False, (244, 35, 232)),
        CityscapesClass("parking", 9, 255, "flat", 1, False, True, (250, 170, 160)),
        CityscapesClass("rail track", 10, 255, "flat", 1, False, True, (230, 150, 140)),
        CityscapesClass("building", 11, 2, "construction", 2, False, False, (70, 70, 70)),
        CityscapesClass("wall", 12, 3, "construction", 2, False, False, (102, 102, 156)),
        CityscapesClass("fence", 13, 4, "construction", 2, False, False, (190, 153, 153)),
        CityscapesClass("guard rail", 14, 255, "construction", 2, False, True, (180, 165, 180)),
        CityscapesClass("bridge", 15, 255, "construction", 2, False, True, (150, 100, 100)),
        CityscapesClass("tunnel", 16, 255, "construction", 2, False, True, (150, 120, 90)),
        CityscapesClass("pole", 17, 5, "object", 3, False, False, (153, 153, 153)),
        CityscapesClass("polegroup", 18, 255, "object", 3, False, True, (153, 153, 153)),
        CityscapesClass("traffic light", 19, 6, "object", 3, False, False, (250, 170, 30)),
        CityscapesClass("traffic sign", 20, 7, "object", 3, False, False, (220, 220, 0)),
        CityscapesClass("vegetation", 21, 8, "nature", 4, False, False, (107, 142, 35)),
        CityscapesClass("terrain", 22, 9, "nature", 4, False, False, (152, 251, 152)),
        CityscapesClass("sky", 23, 10, "sky", 5, False, False, (70, 130, 180)),
        CityscapesClass("person", 24, 11, "human", 6, True, False, (220, 20, 60)),
        CityscapesClass("rider", 25, 12, "human", 6, True, False, (255, 0, 0)),
        CityscapesClass("car", 26, 13, "vehicle", 7, True, False, (0, 0, 142)),
        CityscapesClass("truck", 27, 14, "vehicle", 7, True, False, (0, 0, 70)),
        CityscapesClass("bus", 28, 15, "vehicle", 7, True, False, (0, 60, 100)),
        CityscapesClass("caravan", 29, 255, "vehicle", 7, True, True, (0, 0, 90)),
        CityscapesClass("trailer", 30, 255, "vehicle", 7, True, True, (0, 0, 110)),
        CityscapesClass("train", 31, 16, "vehicle", 7, True, False, (0, 80, 100)),
        CityscapesClass("motorcycle", 32, 17, "vehicle", 7, True, False, (0, 0, 230)),
        CityscapesClass("bicycle", 33, 18, "vehicle", 7, True, False, (119, 11, 32)),
        CityscapesClass("license plate", -1, -1, "vehicle", 7, False, True, (0, 0, 142)),
    ]
    """