import numpy as np
import torch

from grasp_transformer.utils.dataset_processing import image


class CameraData:
    """
    Dataset wrapper for the camera data.
    """
    def __init__(self,
                 width=640,
                 height=480,
                 output_size=224,
                 include_depth=True,
                 include_rgb=True
                 ):
        """
        :param output_size: Image output size in pixels (square)
        :param include_depth: Whether depth image is included
        :param include_rgb: Whether RGB image is included
        """
        self.output_size = output_size
        self.include_depth = include_depth
        self.include_rgb = include_rgb

        if include_depth is False and include_rgb is False:
            raise ValueError('At least one of Depth or RGB must be specified.')

        left = (width - output_size) // 2 #170  640-300
        top = (height - output_size) // 2
        right = (width + output_size) // 2 #470
        bottom = (height + output_size) // 2

        self.bottom_right = (bottom, right)
        self.top_left = (top, left)

    @staticmethod
    def numpy_to_torch(s):
        if len(s.shape) == 2:
            return torch.from_numpy(np.expand_dims(s, 0).astype(np.float32))
        else:
            return torch.from_numpy(s.astype(np.float32))

    def get_depth(self, img):
        depth_img = image.DepthImage(img)
        depth_img.crop(bottom_right=self.bottom_right, top_left=self.top_left)
        depth_img.normalise()
        # depth_img.resize((self.output_size, self.output_size))
        depth_img.img = depth_img.img.transpose((2, 0, 1))
        return depth_img.img

    def get_rgb(self, img, norm=True):
        rgb_img = image.Image(img)
        rgb_img.crop(bottom_right=self.bottom_right, top_left=self.top_left)
        # rgb_img.resize((self.output_size, self.output_size))
        if norm:
                rgb_img.normalise()
                rgb_img.img = rgb_img.img.transpose((2, 0, 1))
        return rgb_img.img

    def get_data(self, rgb=None, depth=None):
        depth_img = None
        rgb_img = None
        # Load the depth image
        if self.include_depth:
            depth_img = self.get_depth(img=depth)
            # depth_img = np.expand_dims(depth_img, axis=0)


        # Load the RGB image
        if self.include_rgb:
            rgb_img = self.get_rgb(img=rgb)

        #包含深度的话需要做一个拼接
        if self.include_depth and self.include_rgb:
            # print(np.expand_dims(depth_img, 0).shape)
            # print(np.expand_dims(rgb_img, 0).shape)
            x = self.numpy_to_torch(
                    np.concatenate(
                        (np.expand_dims(depth_img, 0),
                         np.expand_dims(rgb_img, 0)),
                        axis=1
                    )
                )
        elif self.include_depth:
            # print(np.expand_dims(depth_img, 0).shape)
            x = self.numpy_to_torch(np.expand_dims(depth_img, 0))
        elif self.include_rgb:
            x = self.numpy_to_torch(np.expand_dims(rgb_img, 0))

        return x, depth_img, rgb_img