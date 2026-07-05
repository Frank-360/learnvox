async function startUpgrade() {

    const button = document.getElementById("upgradeButton");

    button.disabled = true;

    button.innerHTML = "⏳ Connecting to Paystack...";

    try {

        const response = await fetch("/pay", {

            method: "POST"

        });

        const data = await response.json();

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