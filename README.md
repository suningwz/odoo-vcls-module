# Kalpa project


 
VCLS customs set of modules.


 
This includes :


 
- [VCLS contact](https://github.com/VCLS-org/odoo-vcls-module/tree/12.0-vcls-module/vcls-contact)


 
- [VCLS helpdesk](https://github.com/VCLS-org/odoo-vcls-module/tree/12.0-vcls-module/vcls-helpdesk)


 
- [VCLS default module](https://github.com/VCLS-org/odoo-vcls-module)


 
- [VCLS hr](https://github.com/VCLS-org/odoo-vcls-module/tree/12.0-vcls-module/vcls-hr)


 
- [VCLS theme](https://github.com/VCLS-org/odoo-vcls-module/tree/12.0-vcls-module/vcls-hr)


 



 
### VCLS branches logic


 
Branch name | Purpose


 
----------- | -------


 
12.0-vcls-module | This is our principal branch which is synchronized with our Odoo instance at https://vcls.odoo.com. Every changes in this branch will directly impact everyone in the company. For these reasons, only GitHub admin can do changes to this branch. It is strongly advised to not edit directly this branch but modify 12.0-vcls-master and then merge 12.0-vcls_master into 12.0-vcls-module.


 
12.0-vcls_master | This is our main development branch. When a new functionality is being developed, every stable version must be committed on this branch until the everything is done. Once this branch is stable enough then Git admins can push the changes to 12.0-vcls-module to release the new version to the entire organization. This branch can be used in order to perform some tests with some key users but it is not intended to be shared within the whole company and is not supposed to be a replacement for 12.0-vcls-module. This branch is managed by Git admins, it is not possible for a normal developer to makes changes to this branch directly. Normal developer must do a “pull request” and be approved by a Git admin in order to modify this branch.


 

        
 ProTip