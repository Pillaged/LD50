import pygame

import prepare


def transform_resource_filename(*filename):
    """ Appends the resource folder name to a filename
    :param filename: String
    :rtype: basestring
    """
    return prepare.fetch(*filename)


def load_image(filename):
    """ Load image from the resources folder

    * Filename will be transformed to be loaded from game resource folder
    * Will be converted if needed.
    """

    filename = transform_resource_filename(filename)
    return pygame.image.load(filename)
