"""
Perlin noise 1D and 2D
"""
import random


def perlin_noise_1d(count, seed, octaves, bias):
    """
    Return a noise 1d array
    """
    perlin_noise = [0.0] * count
    for x in range(count):
        noise = 0.0
        scale = 1.0
        scale_accumulate = 0.0
        for o in range(octaves):
            n_pitch = count >> o
            if n_pitch == 0:
                continue
            n_sample1 = (x / n_pitch) * n_pitch

            # this helps with tessellation
            n_sample2 = (n_sample1 + n_pitch) % count

            # return value between 0 and 1
            blend = float(x - n_sample1) / float(n_pitch)

            sample = (1.0 - blend) * seed[
                n_sample1] + blend * seed[n_sample2]
            noise += sample * scale

            # half the scale so the noise is less strong
            scale_accumulate += scale
            scale /= bias
        perlin_noise[x] = noise / scale_accumulate
    return perlin_noise


def perlin_noise_2d(width, height, seed, octaves, bias):
    """
    Return a perlin 2d noise
    """
    perlin_noise = [0.0] * (width * height)
    for x in range(width):
        for y in range(height):
            noise = 0.0
            scale = 1.0
            scale_accumulate = 0.0
            for o in range(octaves):
                n_pitch = width >> o
                if n_pitch == 0:
                    continue
                n_samplex1 = (x / n_pitch) * n_pitch
                n_sampley1 = (y / n_pitch) * n_pitch

                # this helps with tessellation
                n_samplex2 = (n_samplex1 + n_pitch) % width
                n_sampley2 = (n_sampley1 + n_pitch) % height

                # return value between 0 and 1
                blendx = float(x - n_samplex1) / float(n_pitch)
                blendy = float(y - n_sampley1) / float(n_pitch)

                sample_t = (1.0 - blendx) * seed[
                    n_sampley1 * width + n_samplex1] + blendx * seed[
                    n_sampley1 * width + n_samplex2]

                sample_b = (1.0 - blendx) * seed[
                    n_sampley2 * width + n_samplex1] + blendx * seed[
                    n_sampley2 * width + n_samplex2]

                noise += (blendy * (sample_b - sample_t) + sample_t) * scale

                # half the scale so the noise is less strong
                scale_accumulate += scale
                scale /= bias

            perlin_noise[y * width + x] = noise / scale_accumulate
    return perlin_noise


class PerlinNoise1D(object):
    """
    Model wrapper for perlin noise
    """

    def __init__(self):
        self.noise_seed_1d = []
        self.perlin_noise_1d = []
        self.total_count = 0
        self.total_octaves = 0
        self.bias = 2.0

    def generate_seed(self):
        self.noise_seed_1d = []
        for i in range(self.total_count):
            self.noise_seed_1d.append(random.random())

    def generate_noise(self):
        self.perlin_noise_1d = perlin_noise_1d(
            self.total_count, self.noise_seed_1d, self.total_octaves,
            self.bias)
        return


class PerlinNoise2D(object):
    def __init__(self):
        self.width = 0
        self.height = 0
        self.octaves = 0
        self.bias = 2.0
        self.seed = []
        self.noise = []

    def generate_seed(self):
        seed = []
        for y in range(self.height * self.width + 1):
            seed.append(random.random())
        self.seed = seed

    def generate_noise(self):
        self.noise = perlin_noise_2d(self.width, self.height, self.seed,
                                     self.octaves,
                                     self.bias)
