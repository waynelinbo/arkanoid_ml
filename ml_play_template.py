"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)
import random
from datetime import datetime

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    last_ball_position = [0 ,0]
    final_x = 0
    # speed = 7
    pad = 0
    lastbrick = 0
    is_calcu = False

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()
    random.seed(datetime.now())

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()
        #print(scene_info)

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        delta_x = 0
        # 0:left, 1:right, 2:none
        platform_direction = 0
        # delta_y = 0
        """
        if scene_info.ball[1] >= 393 :
            if final_x < (scene_info.platform[0] + 20) :
                platform_direction = 0
            elif final_x > (scene_info.platform[0] + 20) :
                platform_direction = 1
            else :
                platform_direction = 2
        """
        """if scene_info.ball[1] > 230 :
            if is_speed_up and final_x % 5 != 0 :
                speed += 1
                is_speed_up = False
        else :
            is_speed_up = True"""



        #print(lastbrick)
        if scene_info.frame == 0:
            if (not scene_info.bricks) and (not scene_info.hard_bricks):
                lastbrick = 0
            elif not scene_info.hard_bricks:
                lastbrick = scene_info.bricks[-1][1];
            elif not scene_info.bricks:
                lastbrick = scene_info.hard_bricks[-1][1];
            else:
                if scene_info.bricks[-1][1] > scene_info.hard_bricks[-1][1]:
                    lastbrick = scene_info.bricks[-1][1]
                else:
                    lastbrick = scene_info.hard_bricks[-1][1];


        if scene_info.ball[1] < lastbrick+20 :
            is_calcu = False
            pad = 0


        if last_ball_position[1] < scene_info.ball[1] :
            if (is_calcu == False) and (scene_info.ball[1] > lastbrick+30) :
                delta_x = scene_info.ball[0] - last_ball_position[0]

                if delta_x == -10 :
                    final_x = calculate_position(2, scene_info.ball[0], scene_info.ball[1])
                    is_calcu = True
                    #print(1)
                    pad = 0
                elif delta_x == 10 :
                    final_x = calculate_position(3, scene_info.ball[0], scene_info.ball[1])
                    #print(2)
                    is_calcu = True
                    pad = 0
                elif delta_x == -7 :
                    pad += 1
                    if pad == 3 :
                        #print(3)
                        final_x = calculate_position(0, scene_info.ball[0], scene_info.ball[1])
                        is_calcu = True
                        pad = 0
                elif delta_x == 7 :
                    pad += 1
                    if pad == 3 :
                        #print(4)
                        final_x = calculate_position(1, scene_info.ball[0], scene_info.ball[1])
                        is_calcu = True
                        pad = 0
                """
                elif scene_info.ball[0] < 100 :
                    final_x = calculate_position(1, scene_info.ball[0], scene_info.ball[1])
                    is_calcu = True
                    pad = 0
                else :
                    final_x = calculate_position(0, scene_info.ball[0], scene_info.ball[1])
                    is_calcu = True
                    pad = 0
                """
                # print(final_x)
            
            """
            if final_x < (scene_info.platform[0] + 20) :
                platform_direction = 0
            elif final_x > (scene_info.platform[0] + 20) :
                platform_direction = 1
            else :
                platform_direction = 2
            """
            
            
            # print(final_x)
        else :
            final_x = 100
            # final_x = scene_info.ball[0]
            """
            if scene_info.platform[0] > 80 :
                platform_direction = 0
            elif scene_info.platform[0] < 80:
                platform_direction = 1
            else :
                platform_direction = 2
            """

        if final_x < (scene_info.platform[0] + 20) :
            platform_direction = 0
        elif final_x > (scene_info.platform[0] + 20) :
            platform_direction = 1
        else :
            platform_direction = 2

                    
        last_ball_position = scene_info.ball

        """print(scene_info.bricks[-1], scene_info.hard_bricks[-1])

        if (not scene_info.bricks) and (not scene_info.hard_bricks):
            lastbrick = 400
        elif not scene_info.hard_bricks:
            lastbrick = scene_info.bricks[-1][1];
        elif not scene_info.bricks:
            lastbrick = scene_info.hard_bricks[-1][1];
        else:
            if scene_info.bricks[-1][1] > scene_info.hard_bricks[-1][1]:
                lastbrick = scene_info.bricks[-1][1]
            else:
                lastbrick = scene_info.hard_bricks[-1][1];
        """
        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:
            if platform_direction == 0 :
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            elif platform_direction == 1 :
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            elif platform_direction == 2 :
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)

# 0 : 左下, 1 : 右下
def calculate_position(modes, init_x, init_y) :
    x = init_x
    # y = init_y
    mode = modes
    if mode == 0 or mode == 1 :
        for i in range(init_y, 395) :
            if mode == 0 and x > 0 :
                x-=1
            elif mode == 1 and x < 195 :
                x+=1
            elif mode == 0 and x == 0 :
                x+=1
                mode = 1
            elif mode == 1 and x == 195 :
                x-=1
                mode = 0
    else :
        delta_y = 395 - init_y
        if mode == 2:
            x -= delta_y*10/7
        elif mode == 3:
            x += delta_y*10/7
        # x = int(x)
        while x < 0 or x > 195 :
            if x < 0 :
                x = -x
            else :
                x = 390 - x
            
        """
        for i in range(init_y, 395, 7) :
            if mode == 2 :
                x-=10
                if x < 0 :
                    x = ~x+1
                    mode = 3
                elif x == 0 :
                    mode = 3
            elif mode == 3 :
                x+=10
                if x > 195 :
                    x = 390 - x # 195 - (x-195)
                    mode = 2
                elif x == 195 :
                    mode = 2
        # 剩下的y誤差可算看看
        """

    #print('ox: {:f}'.format(x))
    rr = random.randint(0,1)
    if rr == 0:
        x = float(x)
        x += 2.65
    if rr == 1:
        x = float(x)
        x -= 2.65

    #print('rr: {:d}'.format(rr))
    #print('nx: {:f}'.format(x))
    
    # print(x)
    return x
