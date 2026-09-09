
// =========================
// OPEN BOOKING FORM
// =========================

function openBookingForm() {

    document.getElementById("bookingModal").style.display = "flex";

}


// =========================
// CLOSE BOOKING FORM
// =========================

function closeBookingForm() {

    document.getElementById("bookingModal").style.display = "none";

}


// =========================
// UPDATE PROPERTY PRICE
// =========================

function updatePrice() {

    let propertySelect =
        document.getElementById("propertySelect");

    let selectedOption =
        propertySelect.options[
            propertySelect.selectedIndex
        ];

    let price =
        selectedOption.getAttribute("data-price");

    let amount =
        document.getElementById("bookingAmount");


    if (price) {

        amount.value = price;

    } else {

        amount.value = "";

    }

}


// =========================
// SEARCH BOOKINGS
// =========================

function searchBookings() {

    let searchInput =
        document.getElementById("bookingSearch");

    let searchText =
        searchInput.value.toLowerCase();

    let rows =
        document.querySelectorAll(".booking-row");


    rows.forEach(function(row) {

        let rowText =
            row.innerText.toLowerCase();


        if (rowText.includes(searchText)) {

            row.style.display = "";

        } else {

            row.style.display = "none";

        }

    });

}


// =========================
// CLOSE MODAL WHEN CLICKING
// OUTSIDE THE FORM
// =========================

window.onclick = function(event) {

    let modal =
        document.getElementById("bookingModal");


    if (event.target === modal) {

        closeBookingForm();

    }

};

