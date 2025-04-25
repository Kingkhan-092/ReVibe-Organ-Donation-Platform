// Configuration Constants
const API_CONFIG = {
  baseUrl: "http://localhost:8000",
  endpoints: {
    counts: "/hospitals/fetch-counts",
    appointments: "/hospitals/fetch-appointments",
    appointmentDetails: "/hospitals/fetch-appointment-details",
    appointmentApproval: "/hospitals/appointments-approval/",
    donations: "/hospitals/fetch-donations",
    donationDetails: "/hospitals/fetch-donation-details",
    donationApproval: "/hospitals/donations-approval/",
    searchDonations: "/hospitals/search-donations",
    searchDonationDetails: "/hospitals/search-donation-details",
    viewPdf: "/hospitals/view-pdf/",
    emailDonor: "/hospitals/email-donor/",
    userDetails: "/hospitals/get-user-details",
    updateUserDetails: "/hospitals/update-user-details/",
    updatePassword: "/hospitals/update-pwd-details/"
  },
  carouselInterval: 5000, // 5 seconds
  requestTimeout: 10000 // 10 seconds
};

// DOM Elements
const elements = {
  appointmentCount: document.getElementById("appointmentCount"),
  donationCount: document.getElementById("donationCount"),
  appointDiv: document.getElementById("appointDiv"),
  donationsDiv: document.getElementById("donationsDiv"),
  actionItemTab: document.getElementById("actionItemTab"),
  appointmentTable: document.getElementById("appointmentTable"),
  appointmentTab: document.getElementById("appointmentTab"),
  appointmentsTableBody: document.getElementById("appointmentsTableBody"),
  appointmentDetailsBtn: document.getElementById("appointmentDtls"),
  appointmentAcceptBtn: document.getElementById("appointmentApprv"),
  appointmentDenyBtn: document.getElementById("appointmentDeny"),
  donationTable: document.getElementById("donationTable"),
  donationTab: document.getElementById("donationTab"),
  donationTableBody: document.getElementById("donationTableBody"),
  donationDetailsBtn: document.getElementById("donationDtls"),
  donationAcceptBtn: document.getElementById("donationApprv"),
  donationDenyBtn: document.getElementById("donationDeny"),
  donationSearchTable: document.getElementById("donationSearchTable"),
  searchBtn: document.getElementById("search_btn"),
  userInput: document.getElementById("searchInput"),
  searchTableBody: document.getElementById("searchTableBody"),
  searchDetailsBtn: document.getElementById("searchDtls"),
  searchEmail: document.getElementById("searchEmail"),
  updateProfileTab: document.getElementById("updateProfileTab"),
  hospitalName: document.getElementById("hospitalName"),
  emailHospital: document.getElementById("emailHospital"),
  city: document.getElementById("city"),
  hospitalContact: document.getElementById("hospitalContact"),
  inputProvince: document.getElementById("input-province"),
  password1: document.getElementById("password1"),
  password2: document.getElementById("password2"),
  password3: document.getElementById("password3"),
  passwordValidationMsg: document.getElementById("password-validation-msg"),
  updatePasswordBtn: document.getElementById("update-password"),
  submitUpdateProf: document.getElementById("submitUpdateProf")
};

// State Variables
let state = {
  selectedAppointmentIndex: null,
  selectedDonationIndex: null,
  selectedSearchIndex: null,
  donorName: null,
  donorNameForDonation: null,
  donorToContact: null
};

// Utility Functions
const utils = {
  showLoading: (element) => {
    element.innerHTML = '<div class="spinner">Loading...</div>';
  },

  showError: (error) => {
    console.error(error);
    Swal.fire({
      type: 'error',
      title: 'Error',
      text: 'An unexpected error occurred. Please try again later.'
    });
  },

  makeApiRequest: (method, endpoint, data = null, params = null) => {
    return new Promise((resolve, reject) => {
      const xhttp = new XMLHttpRequest();
      let url = `${API_CONFIG.baseUrl}${endpoint}`;
      
      if (params) {
        url += `?${new URLSearchParams(params).toString()}`;
      }

      xhttp.open(method, url, true);
      xhttp.timeout = API_CONFIG.requestTimeout;

      if (method === 'POST') {
        xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
      }

      xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
          if (this.status === 200) {
            try {
              resolve(JSON.parse(this.responseText));
            } catch (e) {
              resolve(this.responseText);
            }
          } else {
            reject(new Error(`Request failed with status ${this.status}`));
          }
        }
      };

      xhttp.ontimeout = function() {
        reject(new Error('Request timed out'));
      };

      xhttp.onerror = function() {
        reject(new Error('Request failed'));
      };

      xhttp.send(data);
    });
  },

  buildFormData: (obj) => {
    return Object.keys(obj)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(obj[key])}`)
      .join('&');
  },

  clearElement: (element) => {
    while (element.firstChild) {
      element.removeChild(element.firstChild);
    }
  },

  createElement: (tag, attributes = {}, textContent = '') => {
    const element = document.createElement(tag);
    Object.keys(attributes).forEach(attr => {
      element.setAttribute(attr, attributes[attr]);
    });
    if (textContent) {
      element.textContent = textContent;
    }
    return element;
  }
};

// DOM Content Loaded Handler
document.addEventListener("DOMContentLoaded", function() {
  // Initialize carousel
  $('#testimonial-carousel').carousel({
    interval: API_CONFIG.carouselInterval,
    pause: "hover"
  });

  // Initialize event listeners
  initEventListeners();
  
  // Fetch initial counts
  fetchCounts();
});

function initEventListeners() {
  // Check if each element exists before adding event listeners
  if (elements.appointDiv) {
    elements.appointDiv.addEventListener('click', () => {
      $('[href="#appointment_approvals"]').tab('show');
      fetchAppointments();
    });
  }

  if (elements.donationsDiv) {
    elements.donationsDiv.addEventListener('click', () => {
      $('[href="#donation_approvals"]').tab('show');
      fetchDonations();
    });
  }

  if (elements.actionItemTab) {
    elements.actionItemTab.addEventListener("click", fetchCounts);
  }

  // Appointments
  if (elements.appointmentTab) {
    elements.appointmentTab.addEventListener("click", fetchAppointments);
  }

  // if (elements.appointmentDetailsBtn) {
  //   elements.appointmentDetailsBtn.addEventListener("click", detailsOfAppointment);
  // }

  // if (elements.appointmentAcceptBtn) {
  //   elements.appointmentAcceptBtn.addEventListener("click", acceptAppointment);
  // }

  // if (elements.appointmentDenyBtn) {
  //   elements.appointmentDenyBtn.addEventListener("click", denyAppointment);
  // }

  // Donations
  if (elements.donationTab) {
    elements.donationTab.addEventListener("click", fetchDonations);
  }

  if (elements.donationDetailsBtn) {
    elements.donationDetailsBtn.addEventListener("click", detailsOfDonation);
  }

  if (elements.donationAcceptBtn) {
    elements.donationAcceptBtn.addEventListener("click", acceptDonation);
  }

  if (elements.donationDenyBtn) {
    elements.donationDenyBtn.addEventListener("click", denyDonation);
  }

  // Search
  if (elements.searchBtn) {
    elements.searchBtn.addEventListener("click", performSearch);
  }

  if (elements.userInput) {
    elements.userInput.addEventListener("keypress", (event) => {
      if (event.key === "Enter") {
        performSearch();
      }
    });
  }

  if (elements.searchDetailsBtn) {
    elements.searchDetailsBtn.addEventListener("click", searchDetails);
  }

  if (elements.searchEmail) {
    elements.searchEmail.addEventListener("click", emailDonor);
  }

  // Profile
  if (elements.updateProfileTab) {
    elements.updateProfileTab.addEventListener("click", getProfileDetails);
  }

  if (elements.submitUpdateProf) {
    elements.submitUpdateProf.addEventListener("click", updateProfileDetails);
  }

  if (elements.updatePasswordBtn) {
    elements.updatePasswordBtn.addEventListener("click", updatePasswordDetails);
  }

  // Password validation
  if (elements.password2 && elements.password3) {
    elements.password2.addEventListener('input', checkPassword);
    elements.password3.addEventListener('input', checkPassword);
  }
}

// Core Functions
async function fetchCounts() {
  try {
    const data = await utils.makeApiRequest('GET', API_CONFIG.endpoints.counts);
    
    const countOfAppointments = data[0]?.appointment_count || 0;
    const countOfDonations = data[0]?.donation_count || 0;

    if (elements.appointmentCount && elements.donationCount) {
      elements.appointmentCount.textContent = countOfAppointments > 1
        ? `${countOfAppointments} appointments`
        : `${countOfAppointments} appointment`;

      elements.donationCount.textContent = countOfDonations > 1
        ? `${countOfDonations} donations`
        : `${countOfDonations} donation`;
    }
  } catch (error) {
    utils.showError(error);
  }
}

// Make sure to fetch appointments correctly
async function fetchAppointments() {
  try {
    const response = await utils.makeApiRequest('GET', API_CONFIG.endpoints.appointments);
    console.log("Appointments API Response:", response); 
    
    if (response && response.data && Array.isArray(response.data)) {
      displayAppointments(response.data);
      return;
    }
    
    if (response && response.appointments && Array.isArray(response.appointments)) {
      console.warn("Using deprecated response format (appointments)");
      displayAppointments(response.appointments);
      return;
    }
    
    if (Array.isArray(response) && response.length === 0) {
      Swal.fire({
        icon: 'info',
        title: 'No appointments',
        text: 'There are currently no pending appointments'
      });
      return;
    }

    console.error("Invalid appointments data structure:", response);
    throw new Error("Server returned unexpected data format");

  } catch (error) {
    console.error("Fetch appointments error:", error);
    
    if (error.response) {
      switch (error.response.status) {
        case 401:
          return utils.handleUnauthorizedError();
        case 404:
          return Swal.fire({
            icon: 'error',
            title: 'Endpoint not found',
            text: 'The appointments service is currently unavailable'
          });
      }
    }

    Swal.fire({
      icon: 'error',
      title: 'Connection Error',
      text: 'Failed to fetch appointments. Please check your connection and try again.'
    });
  }
}

// Display the fetched appointments in a table
function displayAppointments(appointments) {
  const tableBody = document.getElementById('appointments-table-body');
  tableBody.innerHTML = ''; // Clear existing rows

  appointments.forEach(appointment => {
    const row = document.createElement('tr');

    row.innerHTML = `
      <td>${appointment.appointment_id}</td>
      <td>${appointment.donor_name}</td>
      <td>${appointment.hospital_name}</td>
      <td>${appointment.date}</td>
      <td>${appointment.time}</td>
      <td>
        <button class="btn btn-success btn-sm" onclick="handleAction(${appointment.appointment_id}, 'Approved')">Approve</button>
        <button class="btn btn-danger btn-sm" onclick="handleAction(${appointment.appointment_id}, 'Denied')">Deny</button>
      </td>
    `;
    tableBody.appendChild(row);
  });
}

// Handle action (Approve/Deny) button click
async function handleAction(appointmentId, status) {
  try {
    const response = await utils.makeApiRequest('POST', `${API_CONFIG.endpoints.updateAppointmentStatus}/${appointmentId}/`, {
      status: status
    });

    Swal.fire({
      icon: 'success',
      title: `Appointment ${status}`,
      text: `The appointment has been marked as ${status.toLowerCase()}`
    });

    fetchAppointments(); // Refresh the appointment list
  } catch (error) {
    console.error(`Error updating appointment ${appointmentId}:`, error);
    Swal.fire({
      icon: 'error',
      title: 'Update failed',
      text: `Could not update appointment status. Try again later.`
    });
  }
}

// Handle viewing appointment details
async function viewAppointmentDetails() {
  const selectedAppointment = getSelectedAppointment();
  if (!selectedAppointment) {
    Swal.fire({
      icon: 'warning',
      title: 'No appointment selected',
      text: 'Please select an appointment to view details.'
    });
    return;
  }

  try {
    const appointmentDetails = await utils.makeApiRequest(
      'GET',
      `${API_CONFIG.endpoints.appointmentDetails}/${selectedAppointment.appointment_id}/`
    );

    displayAppointmentDetails(appointmentDetails);
  } catch (error) {
    console.error("Error fetching appointment details:", error);
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Could not fetch appointment details.'
    });
  }
}

// Display the fetched appointment details in a modal or a new section
function displayAppointmentDetails(appointment) {
  const detailsContainer = document.getElementById('appointment-details-container');
  detailsContainer.innerHTML = `
    <h3>Appointment Details</h3>
    <p><strong>First Name:</strong> ${appointment.first_name}</p>
    <p><strong>Last Name:</strong> ${appointment.last_name}</p>
    <p><strong>Email:</strong> ${appointment.email}</p>
    <p><strong>Contact:</strong> ${appointment.contact_number}</p>
    <p><strong>Hospital:</strong> ${appointment.hospital_name}</p>
    <p><strong>Date:</strong> ${appointment.date}</p>
    <p><strong>Time:</strong> ${appointment.time}</p>
    <p><strong>Status:</strong> ${appointment.appointment_status}</p>
  `;
}

// Helper function to get the selected appointment
// function getSelectedAppointment() {
//   const selectedRow = document.querySelector('.appointment-row.selected');
//   if (!selectedRow) {
//     return null;
//   }

//   const appointmentId = selectedRow.getAttribute('data-appointment-id');
//   return { appointment_id: appointmentId };
// }

// Event listener setup for button clicks
// document.getElementById('appointmentApprv').addEventListener('click', () => {
//   const selectedAppointment = getSelectedAppointment();
//   if (selectedAppointment) {
//     handleAction(selectedAppointment.appointment_id, 'Approved');
//   } else {
//     Swal.fire('No appointment selected', 'Please select an appointment to approve.', 'warning');
//   }
// });

// document.getElementById('appointmentDeny').addEventListener('click', () => {
//   const selectedAppointment = getSelectedAppointment();
//   if (selectedAppointment) {
//     handleAction(selectedAppointment.appointment_id, 'Denied');
//   } else {
//     Swal.fire('No appointment selected', 'Please select an appointment to deny.', 'warning');
//   }
// });

// document.getElementById('appointmentDtls').addEventListener('click', () => {
//   viewAppointmentDetails();
// });

async function acceptDonation() {
  if (!isRowSelected('donation')) {
    showSelectionError('donation', 'approve');
    return;
  }

  const donationId = getSelectedId('donation');
  if (!donationId) return;

  try {
    await createPOSTRequest(API_CONFIG.endpoints.donationApproval, false, true, donationId);
    Swal.fire({
      type: 'success',
      title: 'Done',
      text: `${state.donorNameForDonation}'s donation has been approved!`,
      footer: 'Next step: The donation can now be searched under the search donations tab.'
    });
    removeSelectedRow('donation');
  } catch (error) {
    utils.showError(error);
  }
}

async function denyDonation() {
  if (!isRowSelected('donation')) {
    showSelectionError('donation', 'deny');
    return;
  }

  const donationId = getSelectedId('donation');
  if (!donationId) return;

  try {
    await createPOSTRequest(API_CONFIG.endpoints.donationApproval, false, false, donationId);
    Swal.fire("Done", `${state.donorNameForDonation}'s donation has been denied!`, "success");
    removeSelectedRow('donation');
  } catch (error) {
    utils.showError(error);
  }
}

async function detailsOfDonation() {
  if (!isRowSelected('donation')) {
    showSelectionError('donation', 'view details');
    return;
  }

  const donationId = getSelectedId('donation');
  if (!donationId) return;

  try {
    const donation = await utils.makeApiRequest(
      'GET', 
      API_CONFIG.endpoints.donationDetails, 
      null, 
      { donation_id: donationId }
    );
    
    displayDonationDetails(donation);
  } catch (error) {
    utils.showError(error);
  }
}

function displayDonationDetails(donation) {
  const donationDiv = document.getElementById("donation_approvals");
  const existingDetails = document.getElementById("details_of_donation");
  
  if (existingDetails) {
    existingDetails.remove();
  }

  const detailsDiv = createDetailsCard(
    "Donation Details",
    createDetailsGrid(
      createDetailsSection([
        { label: "First Name", value: donation[0].first_name },
        { label: "Last Name", value: donation[0].last_name },
        { label: "Contact Number", value: donation[0].contact_number },
        { label: "Email", value: donation[0].email },
        { label: "City", value: donation[0].city },
        { label: "Country", value: donation[0].country },
        { label: "Province", value: donation[0].province }
      ]),
      createDetailsSection([
        { label: "Donation ID", value: donation[0].donation_id },
        { label: "Donation Status", value: donation[0].donation_status },
        { label: "Organ", value: donation[0].organ },
        { label: "Blood type", value: donation[0].blood_group },
        { label: "Family Member Name", value: donation[0].family_member_name },
        { label: "Family Member Relation", value: donation[0].family_member_relation },
        { label: "Family Member Contact", value: donation[0].family_member_contact }
      ])
    )
  );

  donationDiv.appendChild(detailsDiv);
}

async function performSearch() {
  const searchInput = elements.userInput.value.trim();
  elements.userInput.value = '';

  if (!searchInput) {
    Swal.fire({
      type: 'error',
      title: 'Oops...',
      text: 'Please enter a keyword to search',
      footer: 'Tip: Enter a keyword related to the donation'
    });
    return;
  }

  try {
    const donors = await utils.makeApiRequest(
      'GET', 
      API_CONFIG.endpoints.searchDonations, 
      null, 
      { keyword: searchInput }
    );
    
    if (donors.length <= 0) {
      Swal.fire({
        type: 'info',
        title: 'No donations found',
        text: 'Your search keyword has no donations associated with it.',
      });
    } else {
      displaySearchResults(donors);
    }
  } catch (error) {
    utils.showError(error);
  }
}


function displaySearchResults(donors) {
  utils.clearElement(elements.searchTableBody);

  donors.forEach((donor, index) => {
    const row = utils.createElement('tr', {
      'class': 'selectable_row',
      'data-index': index
    });

    const radioBtn = utils.createElement('input', {
      'type': 'radio',
      'name': 'radioID',
      'class': 'searchRadios'
    });

    row.appendChild(utils.createElement('td', {}, '').appendChild(radioBtn));
    row.appendChild(utils.createElement('td', {}, donor.donation_id));
    row.appendChild(utils.createElement('td', {}, donor.donor));
    row.appendChild(utils.createElement('td', {}, donor.organ));
    row.appendChild(utils.createElement('td', {}, donor.blood_group));

    row.addEventListener("click", () => handleRowSelection(row, index, 'search'));
    elements.searchTableBody.appendChild(row);
  });
}

async function searchDetails() {
  if (!isRowSelected('search')) {
    showSelectionError('donation', 'view details');
    return;
  }

  const donationId = getSelectedId('search');
  if (!donationId) return;

  try {
    const donationDetails = await utils.makeApiRequest(
      'GET', 
      API_CONFIG.endpoints.searchDonationDetails, 
      null, 
      { donation_id: donationId }
    );
    
    displaySearchDetailsResult(donationDetails);
  } catch (error) {
    utils.showError(error);
  }
}

function displaySearchDetailsResult(donationDetails) {
  const searchDiv = document.getElementById("search_donation");
  const existingDetails = document.getElementById("details_of_donation");
  
  if (existingDetails) {
    existingDetails.remove();
  }

  const donorDetailsDiv = createDetailsCard(
    "Donor Details",
    createDetailsGrid(
      createDetailsSection([
        { label: "First Name", value: donationDetails[0].first_name },
        { label: "Last Name", value: donationDetails[0].last_name },
        { label: "Contact Number", value: donationDetails[0].contact_number },
        { label: "Email", value: donationDetails[0].email }
      ]),
      createDetailsSection([
        { label: "City", value: donationDetails[0].city },
        { label: "Country", value: donationDetails[0].country },
        { label: "Province", value: donationDetails[0].province }
      ])
    )
  );

  // Add Donation Details section
  const donationDetailsSection = utils.createElement('div');
  donationDetailsSection.classList.add('card-header', 'bg-light', 'mb-3');
  donationDetailsSection.style.color = 'black';
  donationDetailsSection.textContent = 'Donation Details';

  const donationDetailsBody = utils.createElement('div', { 'class': 'card-body' });
  const donationGrid = createDetailsGrid(
    createDetailsSection([
      { label: "Organ", value: donationDetails[0].organ },
      { label: "Blood Group", value: donationDetails[0].blood_group },
      { label: "Donation Status", value: donationDetails[0].donation_status },
      { label: "Approved by", value: donationDetails[0].approved_by }
    ]),
    createDetailsSection([
      { label: "Family Member Name", value: donationDetails[0].family_member_name },
      { label: "Family Member Relation", value: donationDetails[0].family_member_relation },
      { label: "Family Member Contact", value: donationDetails[0].family_member_contact }
    ])
  );

  donationDetailsBody.appendChild(donationGrid);
  donorDetailsDiv.appendChild(donationDetailsSection);
  donorDetailsDiv.appendChild(donationDetailsBody);

  // Add PDF download button
  const buttonDiv = utils.createElement('div', { 'style': 'text-align: center' });
  const downloadBtn = utils.createElement('button', {
    'class': 'blue buttons',
    'id': 'download_pdf'
  }, 'Download PDF');

  downloadBtn.addEventListener('click', downloadPdf);
  buttonDiv.appendChild(downloadBtn);
  donorDetailsDiv.appendChild(buttonDiv);

  searchDiv.appendChild(donorDetailsDiv);
}

async function downloadPdf() {
  if (!isRowSelected('search')) {
    showSelectionError('donation', 'download PDF');
    return;
  }

  const donationId = getSelectedId('search');
  if (!donationId) return;

  try {
    const url = `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.viewPdf}${donationId}/`;
    window.open(url, '_blank');
  } catch (error) {
    utils.showError(error);
  }
}

async function emailDonor() {
  if (!isRowSelected('search')) {
    showSelectionError('donation', 'email');
    return;
  }

  const donationId = getSelectedId('search');
  if (!donationId) return;

  try {
    await utils.makeApiRequest('GET', `${API_CONFIG.endpoints.emailDonor}${donationId}/`);
    Swal.fire({
      type: 'success',
      title: 'Done',
      text: `An email has been sent to ${state.donorToContact}`,
    });
  } catch (error) {
    utils.showError(error);
  }
}

async function getProfileDetails() {
  try {
    const hospital = await utils.makeApiRequest('GET', API_CONFIG.endpoints.userDetails);
    displayProfileDetails(hospital);
  } catch (error) {
    utils.showError(error);
  }
}

function displayProfileDetails(hospital) {
  if (elements.hospitalName) elements.hospitalName.value = hospital[0].hospital_name;
  if (elements.emailHospital) elements.emailHospital.value = hospital[0].hospital_email;
  if (elements.city) elements.city.value = hospital[0].hospital_city;
  if (elements.hospitalContact) elements.hospitalContact.value = hospital[0].hospital_contact;
  if (elements.inputProvince) elements.inputProvince.value = hospital[0].hospital_province;
}

function checkPassword() {
  if (elements.password2 && elements.password3 && elements.passwordValidationMsg && elements.updatePasswordBtn) {
    if (elements.password2.value === elements.password3.value) {
      elements.passwordValidationMsg.textContent = "Passwords matched!";
      elements.updatePasswordBtn.disabled = false;
    } else {
      elements.passwordValidationMsg.textContent = "Passwords do not match yet!";
      elements.updatePasswordBtn.disabled = true;
    }
  }
}

function enableEditUserProfile() {
  if (elements.hospitalName) elements.hospitalName.disabled = false;
  if (elements.emailHospital) elements.emailHospital.disabled = false;
  if (elements.city) elements.city.disabled = false;
  if (elements.inputProvince) elements.inputProvince.disabled = false;
  if (elements.hospitalContact) elements.hospitalContact.disabled = false;
  if (elements.submitUpdateProf) elements.submitUpdateProf.disabled = false;
}

function enableEditPasswords() {
  if (elements.password1) elements.password1.disabled = false;
  if (elements.password2) elements.password2.disabled = false;
  if (elements.password3) elements.password3.disabled = false;
  if (elements.updatePasswordBtn) elements.updatePasswordBtn.disabled = false;
}

async function updateProfileDetails() {
  const formData = {
    name: elements.hospitalName?.value || '',
    email: elements.emailHospital?.value || '',
    city: elements.city?.value || '',
    contact: elements.hospitalContact?.value || '',
    province: elements.inputProvince?.value || ''
  };

  try {
    await utils.makeApiRequest(
      'POST', 
      API_CONFIG.endpoints.updateUserDetails, 
      utils.buildFormData(formData)
    );
    updateSuccess();
  } catch (error) {
    utils.showError(error);
  }
}

async function updatePasswordDetails() {
  const formData = {
    old_password: elements.password1?.value || '',
    new_password: elements.password2?.value || ''
  };

  try {
    await utils.makeApiRequest(
      'POST', 
      API_CONFIG.endpoints.updatePassword, 
      utils.buildFormData(formData)
    );
    Swal.fire("Done", "Password details updated successfully!", "success");
  } catch (error) {
    utils.showError(error);
  }
}

function updateSuccess() {
  Swal.fire("Done", "Profile details updated successfully!", "success");
}

// Helper Functions
function createDetailsCard(title, content) {
  const card = utils.createElement('div', {
    'class': 'card top',
    'id': title.toLowerCase().includes('appointment') ? 'details_of_appointment' : 'details_of_donation'
  });

  const header = utils.createElement('div', { 'class': 'card-header' }, title);
  const body = utils.createElement('div', { 'class': 'card-body' });

  body.appendChild(content);
  card.appendChild(header);
  card.appendChild(body);

  return card;
}

function createDetailsGrid(...sections) {
  const grid = utils.createElement('div', { 'class': 'details-grid-container' });
  sections.forEach(section => grid.appendChild(section));
  return grid;
}

function createDetailsSection(items) {
  const section = utils.createElement('div', { 'class': 'details-grid-item' });
  items.forEach(item => {
    const p = utils.createElement('p', { 'class': 'card-text' }, `${item.label}: ${item.value}`);
    section.appendChild(p);
  });
  return section;
}

function showSelectionError(type, action) {
  Swal.fire({
    type: 'error',
    title: 'Oops...',
    text: `Please select a ${type} to ${action}!`,
    footer: 'Tip: Click on one of the rows from the table to proceed'
  });
}

function getSelectedId(type) {
  let table, index;
  
  if (type === 'appointment') {
    table = elements.appointmentTable;
    index = state.selectedAppointmentIndex;
  } else if (type === 'donation') {
    table = elements.donationTable;
    index = state.selectedDonationIndex;
  } else {
    table = elements.donationSearchTable;
    index = state.selectedSearchIndex;
  }

  if (index === null || index === undefined || !table) {
    return null;
  }

  // Adjust for header row if present
  const rowIndex = table.rows[0].cells[0].querySelector('input[type="radio"]') ? index + 1 : index;
  return table.rows[rowIndex]?.cells[1]?.textContent || null;
}

function removeSelectedRow(type) {
  let table, index;
  
  if (type === 'appointment') {
    table = elements.appointmentTable;
    index = state.selectedAppointmentIndex;
    state.selectedAppointmentIndex = null;
    state.donorName = null;
  } else if (type === 'donation') {
    table = elements.donationTable;
    index = state.selectedDonationIndex;
    state.selectedDonationIndex = null;
    state.donorNameForDonation = null;
  } else {
    table = elements.donationSearchTable;
    index = state.selectedSearchIndex;
    state.selectedSearchIndex = null;
    state.donorToContact = null;
  }

  if (index !== null && index !== undefined && table) {
    // Adjust for header row if present
    const rowIndex = table.rows[0].cells[0].querySelector('input[type="radio"]') ? index + 1 : index;
    if (table.rows[rowIndex]) {
      table.deleteRow(rowIndex);
    }
  }
}

async function createPOSTRequest(endpoint, isAppointment, isAccept, id) {
  const action = isAccept ? "Approved" : "Denied";
  const data = utils.buildFormData({ ID: id, action });
  
  try {
    await utils.makeApiRequest('POST', endpoint, data);
  } catch (error) {
    throw error;
  }
}