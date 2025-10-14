import os
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_prefix


def generate_launch_description():

    xacro_file = 'barista_robot_model.urdf.xacro'
    package_description = "barista_robot_description"
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_barista_robot = get_package_share_directory(package_description)
    install_dir = get_package_prefix(package_description)

    # Set the path to the WORLD model files. Is to find the models inside the models folder in my_box_bot_gazebo package
    gazebo_models_path = os.path.join(pkg_barista_robot, 'models')
    # os.environ["GAZEBO_MODEL_PATH"] = gazebo_models_path

    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] =  os.environ['GAZEBO_MODEL_PATH'] + ':' + install_dir + '/share' + ':' + gazebo_models_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] =  install_dir + "/share" + ':' + gazebo_models_path

    if 'GAZEBO_PLUGIN_PATH' in os.environ:
        os.environ['GAZEBO_PLUGIN_PATH'] = os.environ['GAZEBO_PLUGIN_PATH'] + ':' + install_dir + '/lib'
    else:
        os.environ['GAZEBO_PLUGIN_PATH'] = install_dir + '/lib'

    print("GAZEBO MODELS PATH=="+str(os.environ["GAZEBO_MODEL_PATH"]))
    print("GAZEBO PLUGINS PATH=="+str(os.environ["GAZEBO_PLUGIN_PATH"]))

    # World arg
    world_arg = DeclareLaunchArgument(
        'world', 
        default_value=[os.path.join(pkg_barista_robot, 'worlds', 'empty.world'), ''], 
        description='SDF world file')

    gazebo_launch_args = {
        'verbose': 'false',
        'pause': 'false',
        'world': LaunchConfiguration('world')
    }

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
        ),
        launch_arguments=gazebo_launch_args.items(),
    )

    include_laser = LaunchConfiguration('include_laser')
    include_laser_arg = DeclareLaunchArgument(
        'include_laser', 
        default_value='true', 
        description='Include laser scanner')
    
    print("Fetching XACRO ==>")
    xacro_urdf_file = os.path.join(pkg_barista_robot, "xacro", xacro_file)

    robot_name_1 = "rick"
    robot_name_2 = "morty"

    # Robot State Publisher
    rsp_robot1 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_robot1',
        namespace=robot_name_1,
        emulate_tty=True,
        parameters=[{'frame_prefix': robot_name_1+'/', 
                    'use_sim_time': True, 
                    'robot_description':  Command(['xacro ', xacro_urdf_file, ' include_laser:=', include_laser, ' robot_name:=', robot_name_1])}],
        output="screen"
    )
    rsp_robot2 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_robot2',
        namespace=robot_name_2,
        emulate_tty=True,
        parameters=[{'frame_prefix': robot_name_2+'/', 
                    'use_sim_time': True, 
                    'robot_description':  Command(['xacro ', xacro_urdf_file, ' include_laser:=', include_laser, ' robot_name:=', robot_name_2])}],
        output="screen"
    )

    # Spawn Robot
    spawn_robot1 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name="spawn_robot1",
        arguments=['-entity', robot_name_1, '-x', '0.0', '-y', '0.0', '-z', '0.0',
                   '-topic', robot_name_1+'/robot_description']
    )
    spawn_robot2 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name="spawn_robot2",
        arguments=['-entity', robot_name_2, '-x', '1.0', '-y', '1.0', '-z', '0.0',
                   '-topic', robot_name_2+'/robot_description']
    )

    # Statif tf from world
    static_tf_robot1 = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_world_robot1',
        arguments=['0', '0', '0', '0', '0', '0', 'world', robot_name_1 + '/odom']
    )
    static_tf_robot2 = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_world_robot2',
        arguments=['1.0', '1.0', '0', '0', '0', '0', 'world', robot_name_2 + '/odom']
    )

    # RVIZ Configuration
    rviz_config_dir = os.path.join(pkg_barista_robot, 'rviz', 'urdf_vis.rviz')

    rviz_node = Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            name='rviz_node',
            parameters=[{'use_sim_time': True}],
            arguments=['-d', rviz_config_dir]
            )

    # create and return launch description object
    return LaunchDescription(
        [
            world_arg,
            gazebo,
            include_laser_arg,
            rsp_robot1,
            rsp_robot2,
            spawn_robot1,
            spawn_robot2,
            static_tf_robot1,
            static_tf_robot2,
            rviz_node
        ]
    )