## Nest_mysql_datalogger

This is project to log nest API data to a mySQL database.  My intention is to eventually play with the data.

The python script can be executed one of two ways: using a config file or with command line arguments.

# Config file

The script can be executed using nest_config.py, which reads in a config file, which has a format laid out in the projects info.config.example.  

Command line arguments:
> -h : display usage information  
> -c : path_to_config_file  
> -d : debug additional verbose information to stdout  
> -x : delete old log files to save space  

# Command line arguments


# Database information
mySQL Database schema and table setups can be found below:

Create a schema:
>CREATE DATABASE `nest` /*!40100 DEFAULT CHARACTER SET latin1 */;

Create the table:
>CREATE TABLE `nest_log` (  
>  `index` int(11) NOT NULL auto_increment,  
>  `trans_time` bit(1) default NULL,  
>  `total_run_time` double default NULL,  
>  `leaf_temp` double default NULL,  
>  `target_type` varchar(45) default NULL,  
>  `total_run_time_away` double default NULL,  
>  `outside_temperature` double default NULL,  
>  `ac_state` varchar(45) default NULL,  
>  `time_stamp` timestamp NULL default NULL,  
>  `current_temperature` double default NULL,  
>  `away` bit(1) default NULL,  
>  `target_temp` double default NULL,  
>  `total_run_time_home` double default NULL,  
>  `fan_state` bit(1) default NULL,  
>  `total_trans_time` double default NULL,  
>  `humidity` double default NULL,  
>  `wind_dir` varchar(10) default NULL,  
>  `wind_mph` double default NULL,  
>  `weather_condition` varchar(45) default NULL,  
>  `heater_state` bit(1) default NULL,  
>  PRIMARY KEY  (`index`)  
>) ENGINE=InnoDB DEFAULT CHARSET=utf8;  



