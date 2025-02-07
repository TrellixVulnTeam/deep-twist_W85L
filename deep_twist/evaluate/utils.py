from deep_twist.data import utils
from shapely.geometry import Polygon
from tqdm import tqdm


def eval_model(args, model, data_loader, progress=False, one_hot=True):
    total_correct = 0
    iter = enumerate(data_loader) 
    if progress:
        iter = tqdm(iter, total=len(data_loader))
    for batch, (rgd, _, pos) in iter:
        rgd = rgd.to(args.device)
        pos = [rect.to(args.device) for rect in pos]
        output = model(rgd)
        if one_hot:
            rects = utils.one_hot_to_rects(*output)
        else:
            rects = output
        total_correct += count_correct(rects, pos)
    return total_correct / len(data_loader.dataset)


def overlap(rect1, rect2):
    poly1 = Polygon(utils.rect_to_points(rect1)) 
    poly2 = Polygon(utils.rect_to_points(rect2))
    intersect = poly1.intersection(poly2).area
    return intersect / (poly1.area + poly2.area - intersect)


def angles_similar(angle1, angle2, thresh):
    mod_diff = (angle2 - angle1) % 180
    return mod_diff <= thresh or mod_diff >= 180 - thresh


def is_successful_grasp(rect, pos):
    for pos_rect in pos:
        is_overlapping = (overlap(rect, pos_rect) > 0.25)
        is_aligned = angles_similar(rect[2], pos_rect[2], 30)
        if is_overlapping and is_aligned:
            return True
    return False


def count_correct(rects, pos):
    correct = 0
    for i in range(len(rects)):
        rect_pos = [rect[i, :] for rect in pos]
        correct += 1 if is_successful_grasp(rects[i], rect_pos) else 0
    return correct
