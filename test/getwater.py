# -*- coding: utf8 -*-
from pprint import pprint

"""access_key_id = 'LTAI2aU1LjHOWKZf'
    #     access_key_secret = 'fe1L3bkeucrrEFnaJbDC5woepupNAv'
    #     mps_region_id = 'cn-hangzhou'
    #     pipeline_id = '264990a3db2b4670812fed84e9d12256'
    #     template_id = 'fae77e4045aa4fa58185619fcf1d341e'
    #     oss_location = 'oss-cn-hangzhou'
    #     oss_bucket = 'jiuban-image'
    #     oss_input_object = 'video/' + str(filename)
    #     oss_output_object = 'video/' + str(filename)"""

import json
from urllib.parse import quote
from aliyunsdkcore.client import AcsClient
from aliyunsdkmts.request.v20140618 import SubmitJobsRequest

def wather(watermark_template_id):
    access_key_id = 'LTAI2aU1LjHOWKZf'
    access_key_secret = 'fe1L3bkeucrrEFnaJbDC5woepupNAv'
    mps_region_id = 'cn-hangzhou'
    pipeline_id = '264990a3db2b4670812fed84e9d12256'
    template_id = 'fae77e4045aa4fa58185619fcf1d341e'
    oss_location = 'oss-cn-hangzhou'
    oss_bucket = 'jiuban-image'
    oss_input_object = 'video/watermarktest1'
    oss_output_object = 'video/watermarktest11'
    image_watermark_object = 'test/water.png'
    video_watermark_object = 'logo.mov'

    # AcsClient
    client = AcsClient(access_key_id, access_key_secret, mps_region_id)
    # request
    request = SubmitJobsRequest.SubmitJobsRequest()
    request.set_accept_format('json')
    # Input
    job_input = {'Location': oss_location,
                 'Bucket': oss_bucket,
                 'Object': quote(oss_input_object)}
    request.set_Input(json.dumps(job_input))
    # Output
    output = {'OutputObject': quote(oss_output_object)}
    # Ouput->TemplateId
    output['TemplateId'] = template_id
    ## Image Watermark
    image_watermark_input = {'Location': oss_location,
                             'Bucket': oss_bucket,
                             'Object': quote(image_watermark_object)}
    image_watermark = {
        'WaterMarkTemplateId': watermark_template_id,
        'Type': 'Image',
        'InputFile': image_watermark_input,
        'ReferPos': 'TopRight',
        'Width': 0.05,
        'Dx': 0,
        'Dy': 0
    }


    # Output->Watermarks
    watermarks = [image_watermark]
    output['WaterMarks'] = watermarks
    # Outputs
    outputs = [output]
    request.set_Outputs(json.dumps(outputs))
    request.set_OutputBucket(oss_bucket)
    request.set_OutputLocation(oss_location)
    # PipelineId
    request.set_PipelineId(pipeline_id)
    # call api
    response_str = client.do_action_with_exception(request)
    response = json.loads(response_str)
    print('RequestId is:', response['RequestId'])
    if response['JobResultList']['JobResult'][0]['Success']:
        print('JobId is:', response['JobResultList']['JobResult'][0]['Job']['JobId'])
    else:
        print('SubmitJobs Failed code:',
              response['JobResultList']['JobResult'][0]['Code'],
              ' message:',
              response['JobResultList']['JobResult'][0]['Message'])