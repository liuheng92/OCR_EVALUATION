#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import namedtuple
import rrc_evaluation_funcs
from rrc_evaluation_funcs import logger
import importlib
import re

def evaluation_imports():
    """
    evaluation_imports: Dictionary ( key = module name , value = alias  )  with python modules used in the evaluation.
    """
    return {
        'Polygon': 'plg',
        'numpy': 'np'
    }


def default_evaluation_params():
    """
    default_evaluation_params: Default parameters to use for the validation and evaluation.
    """
    return {
        'IOU_CONSTRAINT': 0.5,
        'AREA_PRECISION_CONSTRAINT': 0.5,
        'GT_SAMPLE_NAME_2_ID': 'gt_img_([0-9]+).txt',
        'DET_SAMPLE_NAME_2_ID': 'res_img_([0-9]+).txt',
        'LTRB': False,  # LTRB:2points(left,top,right,bottom) or 4 points(x1,y1,x2,y2,x3,y3,x4,y4)
        'CRLF': False,  # Lines are delimited by Windows CRLF format
        'CONFIDENCES': False,  # Detections must include confidence value. AP will be calculated
        'PER_SAMPLE_RESULTS': True,  # Generate per sample results and produce data for visualization
        'E2E': False   #compute average edit distance for end to end evaluation
    }


def validate_data(gtFilePath, submFilePath, evaluationParams):
    """
    Method validate_data: validates that all files in the results folder are correct (have the correct name contents).
                            Validates also that there are no missing files in the folder.
                            If some error detected, the method raises the error
    """
    gt = rrc_evaluation_funcs.load_zip_file(gtFilePath, evaluationParams['GT_SAMPLE_NAME_2_ID'])

    subm = rrc_evaluation_funcs.load_zip_file(submFilePath, evaluationParams['DET_SAMPLE_NAME_2_ID'], True)

    # Validate format of GroundTruth
    for k in gt:
        rrc_evaluation_funcs.validate_lines_in_file(k, gt[k], evaluationParams['CRLF'], evaluationParams['LTRB'], True)

    # Validate format of results
    for k in subm:
        if (k in gt) == False:
            raise Exception("The sample %s not present in GT" % k)

        rrc_evaluation_funcs.validate_lines_in_file(k, subm[k], evaluationParams['CRLF'], evaluationParams['LTRB'],
                                                    evaluationParams['E2E'], evaluationParams['CONFIDENCES'])


def evaluate_method(gtFilePath, submFilePath, evaluationParams):
    """
    Method evaluate_method: evaluate method and returns the results
        Results. Dictionary with the following values:
        - method (required)  Global method metrics. Ex: { 'Precision':0.8,'Recall':0.9 }
        - samples (optional) Per sample metrics. Ex: {'sample1' : { 'Precision':0.8,'Recall':0.9 } , 'sample2' : { 'Precision':0.8,'Recall':0.9 }
    """
    if evaluationParams['E2E']:
        from hanziconv import HanziConv
        import editdistance

    for module, alias in evaluation_imports().iteritems():
        globals()[alias] = importlib.import_module(module)

    def polygon_from_points(points):
        """
        Returns a Polygon object to use with the Polygon2 class from a list of 8 points: x1,y1,x2,y2,x3,y3,x4,y4
        """
        resBoxes = np.empty([1, 8], dtype='int32')
        resBoxes[0, 0] = int(points[0])
        resBoxes[0, 4] = int(points[1])
        resBoxes[0, 1] = int(points[2])
        resBoxes[0, 5] = int(points[3])
        resBoxes[0, 2] = int(points[4])
        resBoxes[0, 6] = int(points[5])
        resBoxes[0, 3] = int(points[6])
        resBoxes[0, 7] = int(points[7])
        pointMat = resBoxes[0].reshape([2, 4]).T
        return plg.Polygon(pointMat)

    def rectangle_to_polygon(rect):
        resBoxes = np.empty([1, 8], dtype='int32')
        resBoxes[0, 0] = int(rect.xmin)
        resBoxes[0, 4] = int(rect.ymax)
        resBoxes[0, 1] = int(rect.xmin)
        resBoxes[0, 5] = int(rect.ymin)
        resBoxes[0, 2] = int(rect.xmax)
        resBoxes[0, 6] = int(rect.ymin)
        resBoxes[0, 3] = int(rect.xmax)
        resBoxes[0, 7] = int(rect.ymax)

        pointMat = resBoxes[0].reshape([2, 4]).T

        return plg.Polygon(pointMat)

    def rectangle_to_points(rect):
        points = [int(rect.xmin), int(rect.ymax), int(rect.xmax), int(rect.ymax), int(rect.xmax), int(rect.ymin),
                  int(rect.xmin), int(rect.ymin)]
        return points

    def get_union(pD, pG):
        areaA = pD.area()
        areaB = pG.area()
        return areaA + areaB - get_intersection(pD, pG)

    def get_intersection_over_union(pD, pG):
        try:
            return get_intersection(pD, pG) / get_union(pD, pG)
        except:
            return 0

    def get_intersection(pD, pG):
        pInt = pD & pG
        if len(pInt) == 0:
            return 0
        return pInt.area()

    def compute_ap(confList, matchList, numGtCare):
        correct = 0
        AP = 0
        if len(confList) > 0:
            confList = np.array(confList)
            matchList = np.array(matchList)
            sorted_ind = np.argsort(-confList)
            confList = confList[sorted_ind]
            matchList = matchList[sorted_ind]
            for n in range(len(confList)):
                match = matchList[n]
                if match:
                    correct += 1
                    AP += float(correct) / (n + 1)

            if numGtCare > 0:
                AP /= numGtCare

        return AP

    #from RTWC17
    def normalize_txt(st):
        """
        Normalize Chinese text strings by:
          - remove puncutations and other symbols
          - convert traditional Chinese to simplified
          - convert English characters to lower cases
        """
        st = ''.join(st.split(' '))
        st = re.sub("\"", "", st)
        # remove any this not one of Chinese character, ascii 0-9, and ascii a-z and A-Z
        new_st = re.sub(ur'[^\u4e00-\u9fa5\u0041-\u005a\u0061-\u007a0-9]+', '', st)
        # convert Traditional Chinese to Simplified Chinese
        new_st = HanziConv.toSimplified(new_st)
        # convert uppercase English letters to lowercase
        new_st = new_st.lower()
        return new_st

    def text_distance(str1, str2):
        str1 = normalize_txt(str1)
        str2 = normalize_txt(str2)
        return editdistance.eval(str1, str2)

    perSampleMetrics = {}

    matchedSum = 0

    Rectangle = namedtuple('Rectangle', 'xmin ymin xmax ymax')

    gt = rrc_evaluation_funcs.load_zip_file(gtFilePath, evaluationParams['GT_SAMPLE_NAME_2_ID'])
    subm = rrc_evaluation_funcs.load_zip_file(submFilePath, evaluationParams['DET_SAMPLE_NAME_2_ID'], True)

    numGlobalCareGt = 0
    numGlobalCareDet = 0

    arrGlobalConfidences = []
    arrGlobalMatches = []

    #total edit distance
    total_dist = 0

    for resFile in gt:

        gtFile = rrc_evaluation_funcs.decode_utf8(gt[resFile])
        recall = 0
        precision = 0
        hmean = 0

        detMatched = 0

        iouMat = np.empty([1, 1])

        gtPols = []
        detPols = []

        gtTrans = []
        detTrans = []

        gtPolPoints = []
        detPolPoints = []

        # Array of Ground Truth Polygons' keys marked as don't Care
        gtDontCarePolsNum = []
        # Array of Detected Polygons' matched with a don't Care GT
        detDontCarePolsNum = []

        pairs = []
        detMatchedNums = []

        arrSampleConfidences = []
        arrSampleMatch = []
        sampleAP = 0

        example_dist = 0
        match_tuples = []

        evaluationLog = ""

        pointsList, _, transcriptionsList = rrc_evaluation_funcs.get_tl_line_values_from_file_contents(gtFile,evaluationParams['CRLF'],evaluationParams['LTRB'],True, False)
        for n in range(len(pointsList)):
            points = pointsList[n]
            transcription = transcriptionsList[n]
            dontCare = (transcription == "###") or (transcription=="?")
            if evaluationParams['LTRB']:
                gtRect = Rectangle(*points)
                gtPol = rectangle_to_polygon(gtRect)
            else:
                gtPol = polygon_from_points(points)
            gtPols.append(gtPol)
            gtPolPoints.append(points)
            gtTrans.append(transcription)
            if dontCare:
                gtDontCarePolsNum.append(len(gtPols) - 1)

        evaluationLog += "GT polygons: " + str(len(gtPols)) + (
        " (" + str(len(gtDontCarePolsNum)) + " don't care)\n" if len(gtDontCarePolsNum) > 0 else "\n")

        if resFile in subm:

            detFile = rrc_evaluation_funcs.decode_utf8(subm[resFile])

            pointsList, confidencesList, transcriptionsList = rrc_evaluation_funcs.get_tl_line_values_from_file_contents(detFile,evaluationParams['CRLF'],evaluationParams['LTRB'],evaluationParams['E2E'],evaluationParams['CONFIDENCES'])
            for n in range(len(pointsList)):
                points = pointsList[n]

                if evaluationParams['LTRB']:
                    detRect = Rectangle(*points)
                    detPol = rectangle_to_polygon(detRect)
                else:
                    detPol = polygon_from_points(points)
                detPols.append(detPol)
                detPolPoints.append(points)
                if evaluationParams['E2E']:
                    transcription = transcriptionsList[n]
                    detTrans.append(transcription)
                if len(gtDontCarePolsNum) > 0:
                    for dontCarePol in gtDontCarePolsNum:
                        dontCarePol = gtPols[dontCarePol]
                        intersected_area = get_intersection(dontCarePol, detPol)
                        pdDimensions = detPol.area()
                        precision = 0 if pdDimensions == 0 else intersected_area / pdDimensions
                        if (precision > evaluationParams['AREA_PRECISION_CONSTRAINT']):
                            detDontCarePolsNum.append(len(detPols) - 1)
                            break

            evaluationLog += "DET polygons: " + str(len(detPols)) + (
            " (" + str(len(detDontCarePolsNum)) + " don't care)\n" if len(detDontCarePolsNum) > 0 else "\n")

            if len(gtPols) > 0 and len(detPols) > 0:
                # Calculate IoU and precision matrixs
                outputShape = [len(gtPols), len(detPols)]
                iouMat = np.empty(outputShape)
                gtRectMat = np.zeros(len(gtPols), np.int8)
                detRectMat = np.zeros(len(detPols), np.int8)
                for gtNum in range(len(gtPols)):
                    for detNum in range(len(detPols)):
                        pG = gtPols[gtNum]
                        pD = detPols[detNum]
                        iouMat[gtNum, detNum] = get_intersection_over_union(pD, pG)

                # match dt index of every gt
                gtMatch = np.empty(len(gtPols), np.int8)
                gtMatch.fill(-1)
                # match gt index of every dt
                dtMatch = np.empty(len(detPols), dtype=np.int8)
                dtMatch.fill(-1)

                for gtNum in range(len(gtPols)):
                    max_iou = 0
                    match_dt_idx = -1

                    for detNum in range(len(detPols)):
                        if gtRectMat[gtNum] == 0 and detRectMat[detNum] == 0\
                                and gtNum not in gtDontCarePolsNum and detNum not in detDontCarePolsNum:
                            if iouMat[gtNum, detNum] > evaluationParams['IOU_CONSTRAINT']:
                                gtRectMat[gtNum] = 1
                                detRectMat[detNum] = 1
                                detMatched += 1
                                pairs.append({'gt': gtNum, 'det': detNum})
                                detMatchedNums.append(detNum)
                                evaluationLog += "Match GT #" + str(gtNum) + " with Det #" + str(detNum) + "\n"

                        if evaluationParams['E2E'] and gtMatch[gtNum] == -1 and dtMatch[detNum] == -1\
                                and gtNum not in gtDontCarePolsNum and detNum not in detDontCarePolsNum:
                            if iouMat[gtNum, detNum] > evaluationParams['IOU_CONSTRAINT'] and iouMat[gtNum, detNum] > max_iou:
                                max_iou = iouMat[gtNum, detNum]
                                match_dt_idx = detNum

                    if evaluationParams['E2E'] and match_dt_idx >= 0:
                        gtMatch[gtNum] = match_dt_idx
                        dtMatch[match_dt_idx] = gtNum

                if evaluationParams['E2E']:
                    for gtNum in range(len(gtPols)):
                        if gtNum in gtDontCarePolsNum:
                            continue
                        gt_text = gtTrans[gtNum]
                        if gtMatch[gtNum] >= 0:
                            dt_text = detTrans[gtMatch[gtNum]]
                        else:
                            dt_text = u''
                        dist = text_distance(gt_text, dt_text)
                        example_dist += dist
                        match_tuples.append((gt_text, dt_text, dist))
                    match_tuples.append(("===============","==============", -1))
                    for detNum in range(len(detPols)):
                        if detNum in detDontCarePolsNum:
                            continue
                        if dtMatch[detNum] == -1:
                            gt_text = u''
                            dt_text = detTrans[detNum]
                            dist = text_distance(gt_text, dt_text)
                            example_dist += dist
                            match_tuples.append((gt_text, dt_text, dist))

            if evaluationParams['CONFIDENCES']:
                for detNum in range(len(detPols)):
                    if detNum not in detDontCarePolsNum:
                        # we exclude the don't care detections
                        match = detNum in detMatchedNums

                        arrSampleConfidences.append(confidencesList[detNum])
                        arrSampleMatch.append(match)

                        arrGlobalConfidences.append(confidencesList[detNum])
                        arrGlobalMatches.append(match)
        #avoid when det file don't exist, example_dist=0
        elif evaluationParams['E2E']:
            match_tuples.append(("===============", "==============", -1))
            dt_text = u''
            for gtNum in range(len(gtPols)):
                if gtNum in gtDontCarePolsNum:
                    continue
                gt_text = gtTrans[gtNum]
                dist = text_distance(gt_text, dt_text)
                example_dist += dist
                match_tuples.append((gt_text, dt_text, dist))
        total_dist += example_dist

        if evaluationParams['E2E']:
            logger.debug('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            logger.debug("file:{}".format(resFile))
            for tp in match_tuples:
                gt_text, dt_text, dist = tp
                logger.debug(u'GT: "{}" matched to DT: "{}", distance = {}'.format(gt_text, dt_text, dist))
            logger.debug('Distance = {:f}'.format(example_dist))
            logger.debug('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')

        numGtCare = (len(gtPols) - len(gtDontCarePolsNum))
        numDetCare = (len(detPols) - len(detDontCarePolsNum))
        if numGtCare == 0:
            recall = float(1)
            precision = float(0) if numDetCare > 0 else float(1)
            sampleAP = precision
        else:
            recall = float(detMatched) / numGtCare
            precision = 0 if numDetCare == 0 else float(detMatched) / numDetCare
            if evaluationParams['CONFIDENCES'] and evaluationParams['PER_SAMPLE_RESULTS']:
                sampleAP = compute_ap(arrSampleConfidences, arrSampleMatch, numGtCare)

        hmean = 0 if (precision + recall) == 0 else 2.0 * precision * recall / (precision + recall)

        matchedSum += detMatched
        numGlobalCareGt += numGtCare
        numGlobalCareDet += numDetCare

        if evaluationParams['PER_SAMPLE_RESULTS']:
            perSampleMetrics[resFile] = {
                'precision': precision,
                'recall': recall,
                'hmean': hmean,
                'pairs': pairs,
                'AP': sampleAP,
                'iouMat': [] if len(detPols) > 100 else iouMat.tolist(),
                'gtPolPoints': gtPolPoints,
                'detPolPoints': detPolPoints,
                'gtDontCare': gtDontCarePolsNum,
                'detDontCare': detDontCarePolsNum,
                'evaluationParams': evaluationParams,
                'evaluationLog': evaluationLog
            }
            if evaluationParams['E2E']:
                perSampleMetrics[resFile]['exampleDistance'] = example_dist
                # print("file:{} exampleDistance:{}".format(resFile,example_dist))

    # Compute MAP and MAR
    AP = 0
    if evaluationParams['CONFIDENCES']:
        AP = compute_ap(arrGlobalConfidences, arrGlobalMatches, numGlobalCareGt)

    methodRecall = 0 if numGlobalCareGt == 0 else float(matchedSum) / numGlobalCareGt
    methodPrecision = 0 if numGlobalCareDet == 0 else float(matchedSum) / numGlobalCareDet
    methodHmean = 0 if methodRecall + methodPrecision == 0 else 2 * methodRecall * methodPrecision / (
    methodRecall + methodPrecision)
    methodDistance = 0 if len(gt) == 0 else float(total_dist)/len(gt)

    methodMetrics = {'precision': methodPrecision, 'recall': methodRecall, 'hmean': methodHmean, 'AP': AP, 'distance': methodDistance}

    resDict = {'calculated': True, 'Message': '', 'method': methodMetrics, 'per_sample': perSampleMetrics}

    return resDict
