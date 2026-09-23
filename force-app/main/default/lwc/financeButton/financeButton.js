import { LightningElement } from 'lwc';
import getMessage from '@salesforce/apex/SalesController.getMessage';

export default class FinanceButton extends LightningElement {
    message;
        
            handleClick() {
                getMessage({ department: 'Finance' })
                    .then((result) => {
                        this.message = result;
                    })
                    .catch((error) => {
                        this.message = 'Error loading message';
                        console.error(error);
                    });
            }
}