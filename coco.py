from pycocotools.coco import COCO
import matplotlib.pyplot as plt
import json

def get_coco_json_format():
    # Standard COCO format 
    coco_format = {
        "info": {},
        "licenses": [],
        "images": [{}],
        "categories": [{}],
        "annotations": [{}]
    }

    return coco_format
    
def coco_json_read(json_file):
    '''
    Given the path of json_file, read the informations of this json
    json_file: the path of the json
    '''
    if type(json_file) is str:
        coco = COCO(json_file)
        print("In json file",json_file)
    else:
        coco = json_file
        

    print("*"*40)

    print("Images:",len(coco.getImgIds()))
    print("Annotations",len(coco.getAnnIds()))

    cat_ids = coco.getCatIds()
    print("Categories:",len(cat_ids))

    for i in cat_ids:
        print("\tCategory",i,":",len(coco.getAnnIds(catIds=[i])))
    
    print("*"*40)
    
def rm_cat_coco(json_path,cat_id):
    '''
    Remove the given category by id of json_path, save it to a new json
    '''
    coco = COCO(json_path)
    print('In original json:')
    coco_json_read(coco) 

    json_ = json.load(open(json_path,'r'))
    coco_format = get_coco_json_format()
    coco_format['info'] = json_['info']
    coco_format['licenses'] = json_['licenses']
    coco_format['images'] = json_['images']
    cats = json_['categories']
    coco_format['categories'] = list(filter(lambda cat:cat['id'] != cat_id,cats))

    rm_cat = list(filter(lambda cat:cat['id'] == cat_id,cats))
    if len(rm_cat) != 1:
        raise BaseException('Does not exist this category in json')
    else:
        rm_cat = rm_cat[0]['name']
    new_json = json_path.split('.')[-2]+'_remove'+rm_cat'.json'

    annIds = coco.getAnnIds()
    # coco.getAnnIds(catIds=[])
    coco_format['annotations'] = list(filter(lambda ann:ann['category_id'] != cat_id,[coco.loadAnns(annId)[0] for annId in annIds]))

    with open(new_json,"w") as outfile:
        json.dump(coco_format, outfile)
    print('Saved removed categroy',cat_id,'json file in',new_json)
    print('In new json:')
    coco_json_read(new_json) 

def rm_empty_im(json_path):
    '''
    Remove images without any annotations of json_path, save it to a new json
    '''    
    coco = COCO(json_path)
    print('In original json:')
    coco_json_read(coco) 

    json_ = json.load(open(json_path,'r'))
    coco_format = get_coco_json_format()
    coco_format['info'] = json_['info']
    coco_format['licenses'] = json_['licenses']
    coco_format['categories'] = json_['categories']
    coco_format['annotations'] = json_['annotations'] 

    new_json = json_path.split('.')[-2]+'_rmempty.json'
    img_infos = []
    drop_num = 0 
    for img_info in json_['images']:
        img_id = img_info['id']
        if len(coco.getAnnIds(imgIds=img_id))>0:
            img_infos.append(img_info)
        else:
            drop_num += 1
    coco_format['images'] =  img_infos    
    print('Removed',drop_num,'images in the json')
    with open(new_json,"w") as outfile:
        json.dump(coco_format, outfile)
    print('Saved dropped empty images json file in',new_json)
    print('In new json:')
    coco_json_read(new_json) 
    
def areas_hist(json_path,splits=5):
    '''
    Visualize the area histograms of the dataset.
    It is a tool for deciding a area threshold as the noise threshold 
    '''
    coco = COCO(json_path)
    annIds = coco.getAnnIds()
    areas = [coco.loadAnns(annId)[0]['area'] for annId in annIds]
    areas.sort()
    
    until = len(areas)
    plt.figure(figsize=(3*splits,3))
    
    for split in range(splits):
        plt.subplot(1,splits,split+1)
        _ = plt.hist(areas[:until],bins=50)
        until = int(until/2)
        plt.xlabel('area')
    plt.show()
    return areas

def rm_noise_coco(json_path,area_thres1,area_thres2=0,visualize = False,image_folder = None):
    '''
    Remove the annotations in the coco with the area in (area_thres2,area_thres1)
    '''
    if visualize and (image_folder is None):
        image_folder = os.path.dirname(json_path)

    coco = COCO(json_path)
    print('In original json:')
    coco_json_read(coco) 

    json_ = json.load(open(json_path,'r'))
    coco_format = get_coco_json_format()
    coco_format['info'] = json_['info']
    coco_format['licenses'] = json_['licenses']
    coco_format['images'] = json_['images']
    coco_format['categories'] = json_['categories']

    new_json = json_path.split('.')[-2]+'_denoise.json'

    imgIds = coco.getImgIds()
    anns = []
    for imgId in imgIds:
        show = False
        show_anns = []
        show_areas = []
        annIds = coco.getAnnIds(imgIds=[imgId])
        for annId in annIds:
            ann = coco.loadAnns(annId)[0]
            if ann['area'] < area_thres1 and ann['area'] > area_thres2 :
                show_anns.append(ann)
                show_areas.append(ann['area'])
                show = True
            else:
                anns.append(ann)
        if visualize:
            im = coco.loadImgs(imgId)[0]['file_name']
            print(im)
            im = os.path.join(image_folder,im)
            im = cv2.imread(im)
            plt.figure(figsize=(8,8))
            plt.imshow(im[:,:,[2,1,0]])
            coco.showAnns(show_anns, True)
            plt.show()
            print(show_areas)
    
    coco_format['annotations'] = anns

    with open(new_json,"w") as outfile:
        json.dump(coco_format, outfile)
    print('In new json:')
    coco_json_read(new_json) 

