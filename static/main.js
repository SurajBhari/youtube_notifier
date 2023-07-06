'use strict';

const applicationServerPublicKey = "BFRgHymBA4XCAjru3nbdulU3CgP3jeSRNKPDluaAdE15HPGniPcdxnqQMCFEH_B11BxSnLkYqESpx1PlPELuk9w";

let isSubscribed = false;
let swRegistration = null;

function urlB64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}


function updateSubscriptionOnServer(subscription) {
    // TODO: Send subscription to application server
}

function subscribeUser() {
    const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
    swRegistration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: applicationServerKey
        })
        .then(function(subscription) {
            console.log('User is subscribed.');
            console.log(subscription)
            updateSubscriptionOnServer(subscription);
            localStorage.setItem('sub_token',JSON.stringify(subscription));
            isSubscribed = true;
            $.ajax({
                type: "POST",
                url: "/subscription/",
                contentType: 'application/json; charset=utf-8',
                dataType:'json',
                data: JSON.stringify({'sub_token':localStorage.getItem('sub_token'), "channel_id": window.location.pathname.split("/")[2]}),
            });
            document.getElementById("status").style.visibility = "visible";
            document.getElementById("status").textContent = "Subscribed";
        })
        .catch(function(err) {
            console.log('Failed to subscribe the user: ', err);
        });
}

function unsubscribeUser() {
    swRegistration.pushManager.getSubscription()
        .then(function(subscription) {
            if (subscription) {
                return subscription.unsubscribe();
            }
        })
        .catch(function(error) {
            console.log('Error unsubscribing', error);
        })
        .then(function() {
            updateSubscriptionOnServer(null);
            console.log('User is unsubscribed.');
            isSubscribed = false;
            $.ajax({
                type: "POST",
                url: "/unsubscription/",
                contentType: 'application/json; charset=utf-8',
                dataType:'json',
                data: JSON.stringify({'sub_token':localStorage.getItem('sub_token'), "channel_id": window.location.pathname.split("/")[2]}),
            });
            document.getElementById("status").style.visibility = "visible";
            document.getElementById("status").textContent = "Unsubscribed";

        });
}

if ('serviceWorker' in navigator && 'PushManager' in window) {
    console.log('Service Worker and Push is supported');

    navigator.serviceWorker.register("/static/sw.js")
        .then(function(swReg) {
            console.log('Service Worker is registered', swReg);
            swRegistration = swReg;
        })
        .catch(function(error) {
            console.error('Service Worker Error', error);
        });
} else {
    console.warn('Push meapplicationServerPublicKeyssaging is not supported');
}

$(document).ready(function(){
    console.log("ready!");
});