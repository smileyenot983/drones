#!/usr/bin/env python

import rospy
import numpy as np
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import TwistStamped

Kp = 0.7
Kd = 0.3

goal_position = '/goal'
current_velocity = '/mavros/local_position/velocity_local'
current_position = '/mavros/local_position/pose'
target_velocity = '/mavros/setpoint_velocity/cmd_vel_unstamped'

def update_u():
    global goal_pos
    global cur_pos
    global goal_pos
    
    ts.header.stamp = rospy.Time.now()

    u_x = Kp*(goal_pos.pose.position.x-cur_pos.pose.position.x) + Kd*(-cur_vel.twist.linear.x ) #* 0.02
    u_y = Kp*(goal_pos.pose.position.y-cur_pos.pose.position.y) + Kd*(-cur_vel.twist.linear.y ) #* 0.02
    u_z = Kp*(goal_pos.pose.position.z-cur_pos.pose.position.z) + Kd*(-cur_vel.twist.linear.z ) #* 0.02
    

    if u_x > 2:
        u_x = 2
    elif u_x < -2:
        u_x = -2
        
    if u_y > 2:
        u_y = 2
    elif u_y < -2:
        u_y = -2
      
    if u_z > 1.5:
        u_z = 1.5
    elif u_z < -1.5:
        u_z = -1.5
        
    #angular part
    g_z_rot = trans_q_to_e(goal_pos)
    c_z_rot = trans_q_to_e(cur_pos)        
    ts.twist.angular.z = Kp*(g_z_rot -c_z_rot) + Kd*(0.0 - cur_vel.twist.angular.z)



    ts.twist.linear.x = u_x
    ts.twist.linear.y = u_y
    ts.twist.linear.z = u_z
 
def checking(msg):
    print(msg)
    
    
def main():
    
    rospy.init_node('talker')
    
    pub = rospy.Publisher('/mavros/setpoint_velocity/cmd_vel',TwistStamped,queue_size=10)
    
    rate = rospy.Rate(50)
    rospy.Subscriber(goal_position,PoseStamped,update_goal)#need to write function
    rospy.Subscriber(current_velocity,TwistStamped,update_cur_vel)#need to write function
    rospy.Subscriber(current_position,PoseStamped,update_cur_pos)#need to write function
    rospy.Subscriber(target_velocity,TwistStamped,checking)

#    cur_pos = PoseStamped()
    global cur_pos 
    cur_pos = PoseStamped()
    
    global cur_vel
    cur_vel = TwistStamped()
    
    global goal_pos
    goal_pos = PoseStamped()
    
    global ts
    ts = TwistStamped()
    ts.header.frame_id = 'map'


    while not rospy.is_shutdown():
        
        update_u()		

        
        
        pub.publish(ts)
        
        
        
        rate.sleep()
    
def trans_q_to_e(obj):
    
    qx = obj.pose.orientation.x
    qy = obj.pose.orientation.y
    qz = obj.pose.orientation.z
    qw = obj.pose.orientation.w   
    
    rotateZa0 = 2.0*(qx*qy + qw*qz)
    rotateZa1 = qw*qw + qx*qx - qy*qy - qz*qz;
    rotateZ = 0.0;
    if rotateZa0 != 0.0 and rotateZa1 != 0.0:
        rotateZ = np.arctan2(rotateZa0, rotateZa1)
    return rotateZ    


def update_cur_pos(msg):
    global cur_pos
    cur_pos = msg

    
def update_cur_vel(msg):	
    global cur_vel
    cur_vel = msg

def update_goal(msg):
    global goal_pos
    goal_pos = msg


 
if __name__=='__main__':
    main()

