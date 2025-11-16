document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('addSubjectForm');
    const message = document.getElementById('formMessage');

    // Handle form submit via AJAX
    if (form && message) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log("Submit intercepted!");
            
            const formData = new FormData(form);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            const response = await fetch("", {
                method: "POST",
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'  
                },
                body: formData
            });

            const data = await response.json();

            const emptyMessage = document.getElementById('empty-message');
            const chooseOption = document.getElementById('choose-option');

            if (data.success) {
                message.textContent = `Subject "${data.subject.name}" added successfully!`;
                form.reset();

                const newSubject = document.createElement('option');
                newSubject.value = `${data.subject.id}`;
                newSubject.textContent = `${data.subject.name}`;

                // Append to the select
                if (emptyMessage) {
                    emptyMessage.insertAdjacentElement('afterend', newSubject);
                    emptyMessage.remove();
                }
                if (chooseOption) {
                    chooseOption.insertAdjacentElement('afterend', newSubject);
                    chooseOption.remove();
                }
            } else {
                message.textContent = data.error;
            }

            setTimeout(() => {
                    message.textContent = '';
            }, 10000);
        });
    }

    // Editor page: Class edit/delete modal functionality
    // Only run if we're on the editor page (check for edit modal)
    const editModal = document.getElementById('editModal');
    if (editModal) {
        let currentClassElement = null;

        // Function to open edit modal with class data
        window.openEditModal = function(element) {
            currentClassElement = element;
            const classId = element.getAttribute('data-class-id');
            const subjectId = element.getAttribute('data-subject-id');
            const day = element.getAttribute('data-day');
            const startTime = element.getAttribute('data-start-time');
            const endTime = element.getAttribute('data-end-time');

            // Populate edit form
            const editClassId = document.getElementById('editClassId');
            const editSubjectSelect = document.getElementById('editSubjectSelect');
            const editClassDay = document.getElementById('editClassDay');
            const editStartTime = document.getElementById('editStartTime');
            const editEndTime = document.getElementById('editEndTime');

            if (editClassId) editClassId.value = classId;
            if (editSubjectSelect) editSubjectSelect.value = subjectId;
            if (editClassDay) editClassDay.value = day;
            if (editStartTime) editStartTime.value = startTime;
            if (editEndTime) editEndTime.value = endTime;

            // Open edit modal
            const modal = new bootstrap.Modal(editModal);
            modal.show();
        };

        // Handle edit button click (from top buttons)
        const editButton = document.querySelector('[data-bs-target="#editModal"]');
        if (editButton) {
            editButton.addEventListener('click', function(e) {
                // If no class is selected, prevent opening modal
                if (!currentClassElement) {
                    e.preventDefault();
                    alert('Please click on a class to edit it first.');
                }
            });
        }

        // Handle delete button click (from top buttons)
        const deleteButton = document.querySelector('[data-bs-target="#deleteModal"]');
        const deleteModal = document.getElementById('deleteModal');
        if (deleteButton && deleteModal) {
            deleteButton.addEventListener('click', function(e) {
                // If no class is selected, prevent opening modal
                if (!currentClassElement) {
                    e.preventDefault();
                    alert('Please click on a class to delete it first.');
                } else {
                    // Populate delete modal
                    const classId = currentClassElement.getAttribute('data-class-id');
                    const subjectName = currentClassElement.getAttribute('data-subject-name');
                    const day = currentClassElement.getAttribute('data-day');
                    const startTime = currentClassElement.getAttribute('data-start-time');
                    const endTime = currentClassElement.getAttribute('data-end-time');

                    // Format day name
                    const dayNames = {
                        'SUN': 'Sunday',
                        'MON': 'Monday',
                        'TUE': 'Tuesday',
                        'WED': 'Wednesday',
                        'THU': 'Thursday',
                        'FRI': 'Friday',
                        'SAT': 'Saturday'
                    };

                    // Format time
                    function formatTime(time24) {
                        const [hours, minutes] = time24.split(':');
                        const hour = parseInt(hours);
                        const ampm = hour >= 12 ? 'PM' : 'AM';
                        const hour12 = hour % 12 || 12;
                        return `${hour12}:${minutes} ${ampm}`;
                    }

                    const deleteClassId = document.getElementById('deleteClassId');
                    const deleteSubjectName = document.getElementById('deleteSubjectName');
                    const deleteClassDay = document.getElementById('deleteClassDay');
                    const deleteClassTime = document.getElementById('deleteClassTime');

                    if (deleteClassId) deleteClassId.value = classId;
                    if (deleteSubjectName) deleteSubjectName.textContent = subjectName;
                    if (deleteClassDay) deleteClassDay.textContent = dayNames[day] || day;
                    if (deleteClassTime) deleteClassTime.textContent = `${formatTime(startTime)} - ${formatTime(endTime)}`;
                }
            });
        }
    }
});