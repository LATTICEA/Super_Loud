var a = new XMLHttpRequest();
a.open("GET","/run-subscription-payment-routine");
a.send();

"use strict";
const d = document;
d.addEventListener("DOMContentLoaded", function(event) {
    
    // Pricing countup
    var billingSwitchEl = d.getElementById('billingSwitch');

    var cancel_at = document.getElementById('cancel_at').value;
    var subtype = document.getElementById('subtype').value;
    var pertype = document.getElementById('pertype').value;
    var envtype = document.getElementById('env').value;

    if (envtype == 'dev'){
        var month = 1;
        var year = 10;
    } else {
        var month = 1500;
        var year = 15000;
    }

    if(billingSwitchEl) {

        if (pertype == 'Annually') {
            billingSwitch.checked = true;
            countUpPremium1 = new countUp.CountUp('pricePremium1', month, { startVal: year });
        } else {
            billingSwitch.checked = false;
            countUpPremium1 = new countUp.CountUp('pricePremium1', year, { startVal: month });

            if(pertype != 'Monthly' && cancel_at == 'None' && subtype == 'Data+Predictions') {
                document.getElementById('dp-sub-btn').innerText = 'Switch to monthly billing';
            } else if (pertype != 'Monthly' && cancel_at != 'None' && subtype == 'Data+Predictions') {
                document.getElementById('dp-sub-btn').innerText = 'Reinstate subscription with monthly billing (Current monthly plan cancels on ' + cancel_at.toString() + ')';
            } else if (pertype == 'Monthly' && cancel_at != 'None' && subtype == 'Data+Predictions') {
                document.getElementById('dp-sub-btn').innerText = 'Reinstate subscription (Cancels on ' + cancel_at.toString() + ')';
            } else if (pertype == 'Monthly' && cancel_at == 'None' && subtype == 'Data+Predictions') {
                document.getElementById('dp-sub-btn').innerText = 'Cancel monthly subscription';
            } else {
                document.getElementById('dp-sub-btn').innerText = 'Subscribe';
            }
        }

        billingSwitchEl.addEventListener('change', function() {
            if(billingSwitch.checked) {
                    if(pertype != 'Annually' && cancel_at == 'None' && subtype == 'Data+Predictions') {
                        document.getElementById('dp-sub-btn').innerText = 'Switch to annual billing';
                    } else if (pertype != 'Annually' && cancel_at != 'None' && subtype == 'Data+Predictions') {
                        document.getElementById('dp-sub-btn').innerText = 'Reinstate subscription with annual billing (Current annual plan cancels on ' + cancel_at.toString() + ')';
                    } else if (pertype == 'Annually' && cancel_at != 'None' && subtype == 'Data+Predictions') {
                        document.getElementById('dp-sub-btn').innerText = 'Reinstate subscription (Cancels on ' + cancel_at.toString() + ')';
                    } else if (pertype == 'Annually' && cancel_at == 'None' && subtype == 'Data+Predictions') {
                        document.getElementById('dp-sub-btn').innerText = 'Cancel annual subscription';
                    } else {
                        document.getElementById('dp-sub-btn').innerText = 'Subscribe';
                    }
                setTimeout(function () {
                    countUpPremium1 = new countUp.CountUp('pricePremium1', month, { startVal: year });
                }, 100);
                document.getElementById('billingSwitch').disabled = true;
                countUpPremium1.start();
                document.getElementById('billingSwitch').disabled = false;

                document.getElementById('switchvalue').value = 'y';
            } else {
                    if (pertype != 'Monthly' && cancel_at == 'None' && subtype == 'Data+Predictions') {
                        document.getElementById('dp-sub-btn').innerText = 'Switch to monthly billing';
                    } else if (pertype != 'Monthly' && cancel_at != 'None' && subtype == 'Data+Predictions') {
                        document.getElementById('dp-sub-btn').innerText = 'Reinstate subscription with monthly billing (Current monthly plan cancels on ' + cancel_at.toString() + ')';
                    } else if (pertype == 'Monthly' && cancel_at != 'None' && subtype == 'Data+Predictions') {
                        document.getElementById('dp-sub-btn').innerText = 'Reinstate subscription (Cancels on ' + cancel_at.toString() + ')';
                    } else if (pertype == 'Monthly' && cancel_at == 'None' && subtype == 'Data+Predictions') {
                        document.getElementById('dp-sub-btn').innerText = 'Cancel monthly subscription';
                    } else {
                        document.getElementById('dp-sub-btn').innerText = 'Subscribe';
                    }
                setTimeout(function () {
                    countUpPremium1 = new countUp.CountUp('pricePremium1', year, { startVal: month });
                }, 100);
                document.getElementById('billingSwitch').disabled = true;
                countUpPremium1.start();
                document.getElementById('billingSwitch').disabled = false;

                document.getElementById('switchvalue').value = 'm';
            }
        });
    }
});