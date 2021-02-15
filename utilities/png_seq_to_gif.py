"""
Convert a png sequence of a animated gif used for presenting the experiments
"""
import os
import sys

import imageio


def main():
    png_dir = sys.argv[1]
    images = []
    for i, file_name in enumerate(sorted(os.listdir(png_dir))):
        if i % 10 == 0:
            print(file_name)
            if file_name.endswith('.png'):
                file_path = os.path.join(png_dir, file_name)
                images.append(imageio.imread(file_path))
    last_image = images[-1]
    for i in range(5):
        images.append(last_image)
    imageio.mimsave(sys.argv[2], images)


if __name__ == '__main__':
    main()
