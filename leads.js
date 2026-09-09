
function openLeadForm() {
    document.getElementById("leadModal").style.display = "flex";
}


function closeLeadForm() {
    document.getElementById("leadModal").style.display = "none";
}


/* SEARCH */

function searchLeads() {

    let input =
        document.getElementById("searchInput")
        .value
        .toLowerCase();

    let rows =
        document.querySelectorAll(".lead-row-data");

    rows.forEach(function(row) {

        let text =
            row.innerText.toLowerCase();

        if (text.includes(input)) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }

    });
}


/* FILTER */

function filterLeads() {

    let selectedStage =
        document.getElementById("stageFilter").value;

    let rows =
        document.querySelectorAll(".lead-row-data");

    rows.forEach(function(row) {

        let stage =
            row.getAttribute("data-stage");

        if (
            selectedStage === "all" ||
            stage === selectedStage
        ) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }

    });
}


/* OPEN EDIT MODAL */

function openEditLead(
    id,
    name,
    phone,
    email,
    source,
    stage,
    assignedTo,
    notes,
    followUpDate
) {

    document.getElementById("editLeadModal")
        .style.display = "flex";


    document.getElementById("editName")
        .value = name;

    document.getElementById("editPhone")
        .value = phone;

    document.getElementById("editEmail")
        .value = email;

    document.getElementById("editSource")
        .value = source;

    document.getElementById("editStage")
        .value = stage;

    document.getElementById("editAssigned")
        .value = assignedTo;

    document.getElementById("editNotes")
        .value = notes;

    document.getElementById("editFollowUp")
        .value = followUpDate;


    document.getElementById("editLeadForm")
        .action = "/edit-lead/" + id;
}


/* CLOSE EDIT MODAL */

function closeEditLead() {

    document.getElementById("editLeadModal")
        .style.display = "none";
}


/* CLOSE MODAL WHEN CLICKING OUTSIDE */

window.addEventListener("click", function(event) {

    let editModal =
        document.getElementById("editLeadModal");

    let addModal =
        document.getElementById("leadModal");


    if (event.target === editModal) {
        closeEditLead();
    }

    if (event.target === addModal) {
        closeLeadForm();
    }

});

