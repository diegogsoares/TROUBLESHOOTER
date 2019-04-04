# TROUBLESHOOTER

This project was create with an intent of having some troubleshooting capabilities automated for a large number of network devices.

## Getting Started

This folder is structured as following:

config - Where inventory file is


### Prerequisites

   - MAC, Linux (not supported on Windows)
   - python 3.x
   - pip package manager (https://pip.pypa.io/en/stable/installing/)
```bash
   If already installed, make sure that pip / setuptools are upto date (commands may vary)
   
   pip install --upgrade pip
   
   Ubuntu: sudo pip install --upgrade setuptools
```
   - virtualenv (recommended)
```bash
   Ubuntu: sudo apt-get install python-virtualenv
   Fedora: sudo dnf install python-virtualenv
   MAC: sudo pip install virtualenv
```

### Installing

Clone git repository
```bash
   git https://github.com/diegogsoares/TROUBLESHOOTER.git
   cd TROUBLESHOOTER
   python3 -m pip install -r requirements.txt 
   
```

## Deployment

Edit the inventory file inside config folder with proper Credentials, Site Names, IP Ranges and Switches information.

NOTE: all file references should consider the base folder being TROUBLESHOOTER. (Ex: inventory file is config/inventory.json)
```
{
	"Sites": [
		{
		"site_name": "New York City",
		"site_code": "NYC",
		"site_ip_range": "10.10.0.0/16",
		"switch_username": "admin",
		"switch_password": "cisco123",		
		"switches": [
			{ "switch_ip": "10.10.200.1", "switch_name": "NYC-Core01", "switch_group": "core" },
			{ "switch_ip": "10.10.200.2", "switch_name": "NYC-Core01", "switch_group": "core" },
			{ "switch_ip": "10.10.3.3", "switch_name": "NYC-Access01", "switch_group": "access" },
			{ "switch_ip": "10.10.3.4", "switch_name": "NYC-Access02", "switch_group": "access" },
			{ "switch_ip": "10.10.3.5", "switch_name": "NYC-Access03", "switch_group": "access" }
		]
		},
		{
			"site_name": "San Francisco",
			"site_code": "SFO",
			"site_ip_range": "10.11.0.0/16",
			"switch_username": "admin",
			"switch_password": "cisco123",		
			"switches": [
				{ "switch_ip": "10.11.200.1", "switch_name": "SFO-Core01", "switch_group": "core" },
				{ "switch_ip": "10.11.200.2", "switch_name": "SFO-Core01", "switch_group": "core" },
				{ "switch_ip": "10.11.3.3", "switch_name": "SFO-Access01", "switch_group": "access" },
				{ "switch_ip": "10.11.3.4", "switch_name": "SFO-Access02", "switch_group": "access" },
				{ "switch_ip": "10.11.3.5", "switch_name": "SFO-Access03", "switch_group": "access" }
			]
		}
	]
}
```
To add more sites or switches just edit the json file accordinly 
## Running Troubleshooter



## Built With

* [PyCharm CE](https://www.jetbrains.com/pycharm/) - Python IDE

## Contributing

none

## Authors

* **Diego Soares** - *Initial work* - [diegogsoares](https://github.com/diegogsoares)

See also the list of [contributors] who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* BIG THANK YOU to all my CISCO customers that challenged me with use cases.

