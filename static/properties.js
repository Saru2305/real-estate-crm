
function openPropertyForm() {
    document.getElementById("propertyModal").style.display = "flex";
}

function closePropertyForm() {
    document.getElementById("propertyModal").style.display = "none";
}


/* SEARCH */

function searchProperties() {

    let search =
        document.getElementById("propertySearch")
        .value
        .toLowerCase();

    let rows =
        document.querySelectorAll(".property-row");

    rows.forEach(function(row) {

        let text = row.innerText.toLowerCase();

        row.style.display =
            text.includes(search) ? "" : "none";

    });
}


/* FILTER */

function filterProperties() {

    let search =
        document.getElementById("propertySearch")
        .value
        .toLowerCase();

    let selectedStatus =
        document.getElementById("propertyStatus").value;

    let selectedType =
        document.getElementById("propertyType").value;

    let rows =
        document.querySelectorAll(".property-row");


    rows.forEach(function(row) {

        let text =
            row.innerText.toLowerCase();

        let status =
            row.getAttribute("data-status");

        let type =
            row.getAttribute("data-type");


        let matchesSearch =
            text.includes(search);

        let matchesStatus =
            selectedStatus === "all" ||
            status === selectedStatus;

        let matchesType =
            selectedType === "all" ||
            type === selectedType;


        if (
            matchesSearch &&
            matchesStatus &&
            matchesType
        ) {

            row.style.display = "";

        } else {

            row.style.display = "none";

        }

    });
}


/* COUNT PROPERTY STATUS */

document.addEventListener("DOMContentLoaded", function() {

    let rows =
        document.querySelectorAll(".property-row");

    let available = 0;
    let booked = 0;


    rows.forEach(function(row) {

        let status =
            row.getAttribute("data-status");

        if (status === "Available") {
            available++;
        }

        if (status === "Booked") {
            booked++;
        }

    });


    document.getElementById("availableCount").textContent =
        available;

    document.getElementById("bookedCount").textContent =
        booked;

});


/* CLOSE MODAL */

window.onclick = function(event) {

    let modal =
        document.getElementById("propertyModal");

    if (event.target === modal) {
        closePropertyForm();
    }

};
``
