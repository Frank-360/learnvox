async function startUpgrade() {

    console.log("startUpgrade() has started");

    const button = document.getElementById("upgradeButton");

    button.disabled = true;

    button.innerHTML = "⏳ Connecting to Paystack...";

    try {

        console.log("About to call /pay");

        const response = await fetch("/pay", {

            method: "POST"

        });

        console.log("Response received:", response.status);

        const data = await response.json();

        console.log("Response data:", data);

        if (!data.success) {

            alert(data.message);

            button.disabled = false;

            button.innerHTML = "🚀 Become a Founding Member";

            return;

        }

        window.location.href = data.checkout_url;

    }

    catch(error){

        console.error(error);

        alert("Unable to connect to Paystack.");

        button.disabled = false;

        button.innerHTML = "🚀 Become a Founding Member";

    }

}