import { LightningElement } from 'lwc';
import getMessage from '@salesforce/apex/SalesController.getMessage';


export default class MarketingButton extends LightningElement {
    message;
    
        handleClick() {
            getMessage({ department: 'Marketing' })
                .then((result) => {
                    this.message = result;
                })
                .catch((error) => {
                    this.message = 'Error loading message';
                    console.error(error);
                });
        }
}