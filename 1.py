from ffmpy import FFmpeg


import ctypes

ff = FFmpeg(inputs={video_path: None},
                outputs={out_path: '-f image2 -vf fps=fps={},scale=180*75,tile=10x10'.format(fps_r),
                         out_path2: '-y -f mjpeg -ss 0 -t 0.001',
                         None: '-c copy -map 0 -y -f segment -segment_list {0} -segment_time 1  -bsf:v h264_mp4toannexb  {1}/cat_output%03d.ts'.format(
                             out_path3, base_path),
                         })

print(ff.cmd)
ff.run()
