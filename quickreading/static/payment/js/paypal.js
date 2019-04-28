// reference https://developer.paypal.com/docs/checkout/integrate/#  https://codepen.io/adamstuartclark/pen/pbYVYR
paypal.Button.render({
    env: 'sandbox', // Or 'production'
    commit: true,
    locale: 'en_US',
    style: {
        size: 'large',
        color: 'gold',
        layout: 'vertical',
        shape: 'pill',
        label: 'checkout',
    },
    funding: {
        allowed: [paypal.FUNDING.CARD],
        disallowed: [paypal.FUNDING.CREDIT]
    },
    payment: function () {
        // 2. Make a request to your server
        if (document.getElementById("control_01").checked) {
            return paypal.request.post('http://0.0.0.0:8001/payOneMonth')
                .then(function (data) {
                    // 3. Return res.id from the response
                    return data.paymentID;
                });
        }
        if (document.getElementById("control_02").checked) {
            return paypal.request.post('http://0.0.0.0:8001/paySixMonth')
                .then(function (data) {
                    // 3. Return res.id from the response
                    return data.paymentID;
                });
        }
        if (document.getElementById("control_03").checked) {
            return paypal.request.post('http://0.0.0.0:8001/payOneYear')
                .then(function (data) {
                    // 3. Return res.id from the response
                    return data.paymentID;
                });
        }
    },
    // Execute the payment:
    onAuthorize: function (data) {
        if (document.getElementById("control_01").checked) {
            // 2. Make a request to your server
            return paypal.request.post('http://0.0.0.0:8001/executeOneMonth', {
                paymentID: data.paymentID,
                payerID: data.payerID
            })
                .then(function (res) {
                    //already paied
                    console.log(res.success)
                    var msg = "You have paid one month vip service!";
                    if (confirm(msg)) {
                        window.location.href = '/user/personal/info';
                    }
                });
        }
        if (document.getElementById("control_02").checked) {
            // 2. Make a request to your server
            return paypal.request.post('http://0.0.0.0:8001/executeSixMonth', {
                paymentID: data.paymentID,
                payerID: data.payerID
            })
                .then(function (res) {
                    //already paied
                    console.log(res.success)
                    var msg = "You have paid six months vip service!";
                    if (confirm(msg)) {
                        window.location.href = '/user/personal/info';
                    }
                });
        }
        if (document.getElementById("control_03").checked) {
            // 2. Make a request to your server
            return paypal.request.post('http://0.0.0.0:8001/executeOneYear', {
                paymentID: data.paymentID,
                payerID: data.payerID
            })
                .then(function (res) {
                    //already paied
                    console.log(res.success)
                    var msg = "You have paid one year vip service!";
                    if (confirm(msg)) {
                        window.location.href = '/user/personal/info';
                    }
                });
        }
    }
}, '#paypal-button');
