document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('addSubjectForm');
    const message = document.getElementById('formMessage');
    const addClassForm = document.getElementById('addClassForm');
    const editClassForm = document.getElementById('editClassForm');
    const addClassError = document.getElementById('addClassError');
    const editClassError = document.getElementById('editClassError');

    const toMinutes = (value) => {
        if (!value || typeof value !== 'string' || !value.includes(':')) {
            return null;
        }
        const [hours, minutes] = value.split(':').map(Number);
        if (Number.isNaN(hours) || Number.isNaN(minutes)) {
            return null;
        }
        return (hours * 60) + minutes;
    };

    const scheduleRegistry = (() => {
        const collect = () => Array.from(document.querySelectorAll('.class-block[data-day]')).map((node) => ({
            id: Number(node.dataset.classId),
            day: node.dataset.day,
            start: node.dataset.start,
            end: node.dataset.end
        }));

        let cache = collect();

        const refresh = () => {
            cache = collect();
        };

        const findConflict = (day, startMinutes, endMinutes, ignoreId) => cache.find((schedule) => {
            if (!schedule.day || schedule.day !== day) {
                return false;
            }
            if (ignoreId && schedule.id === Number(ignoreId)) {
                return false;
            }
            const scheduleStart = toMinutes(schedule.start);
            const scheduleEnd = toMinutes(schedule.end);
            if (scheduleStart === null || scheduleEnd === null) {
                return false;
            }
            return scheduleStart < endMinutes && scheduleEnd > startMinutes;
        });

        return { refresh, findConflict };
    })();

    const showAlert = (element, text) => {
        if (!element) return;
        element.textContent = text;
        element.classList.remove('d-none');
    };

    const hideAlert = (element) => {
        if (!element) return;
        element.textContent = '';
        element.classList.add('d-none');
    };

    const validateScheduleInput = ({ day, start, end, ignoreId }) => {
        if (!day) {
            return { valid: false, message: 'Please choose a day for the class.' };
        }

        const startMinutes = toMinutes(start);
        const endMinutes = toMinutes(end);

        if (startMinutes === null || endMinutes === null) {
            return { valid: false, message: 'Please provide a valid start and end time.' };
        }

        if (startMinutes >= endMinutes) {
            return { valid: false, message: 'End time must be later than start time.' };
        }

        const conflict = scheduleRegistry.findConflict(day, startMinutes, endMinutes, ignoreId);
        if (conflict) {
            return {
                valid: false,
                message: `Conflicts with an existing class from ${conflict.start} to ${conflict.end}.`
            };
        }

        return { valid: true };
    };

    if (addClassForm) {
        addClassForm.addEventListener('submit', (e) => {
            const validation = validateScheduleInput({
                day: addClassForm.elements['classDay']?.value,
                start: addClassForm.elements['startTime']?.value,
                end: addClassForm.elements['endTime']?.value
            });

            if (!validation.valid) {
                e.preventDefault();
                showAlert(addClassError, validation.message);
                return;
            }

            hideAlert(addClassError);
            scheduleRegistry.refresh();
        });
    }

    // Handle form submit via AJAX
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

    // Handle class-block clicks to populate edit modal
    const editModal = document.getElementById('editModal');
    if (editModal) {
        editModal.addEventListener('show.bs.modal', async function (event) {
            // Get the button that triggered the modal
            const button = event.relatedTarget;
            
            // Check if it's a class-block with data-class-id
            const classId = button ? button.getAttribute('data-class-id') : null;
            
            if (classId) {
                // Fetch class data
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                try {
                    const response = await fetch(`?getClass=1&editClassId=${classId}`, {
                        method: 'GET',
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        const classData = data.class;
                        
                        // Populate the edit form
                        document.getElementById('editClassId').value = classData.id;
                        document.getElementById('editSubjectSelect').value = classData.subject_id;
                        document.getElementById('editClassDay').value = classData.day_of_week;
                        document.getElementById('editStartTime').value = classData.start_time;
                        document.getElementById('editEndTime').value = classData.end_time;
                    } else {
                        console.error('Error fetching class data:', data.error);
                    }
                } catch (error) {
                    console.error('Error fetching class data:', error);
                }
            } else {
                document.getElementById('editClassId').value = '';
                document.getElementById('editSubjectSelect').selectedIndex = 0;
                document.getElementById('editClassDay').selectedIndex = 0;
                document.getElementById('editStartTime').value = '';
                document.getElementById('editEndTime').value = '';
            }
        });
    }

    // Handle edit class form submission via AJAX
    if (editClassForm) {
        editClassForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const validation = validateScheduleInput({
                day: editClassForm.elements['editClassDay']?.value,
                start: editClassForm.elements['editStartTime']?.value,
                end: editClassForm.elements['editEndTime']?.value,
                ignoreId: editClassForm.elements['editClassId']?.value
            });

            if (!validation.valid) {
                showAlert(editClassError, validation.message);
                return;
            }

            hideAlert(editClassError);

            const formData = new FormData(editClassForm);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            try {
                const response = await fetch("", {
                    method: "POST",
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    // Close the modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editModal'));
                    if (modal) {
                        modal.hide();
                    }
                    // Reload the page to show updated data
                    window.location.reload();
                } else {
                    alert('Error: ' + (data.error || 'Failed to update class'));
                }
            } catch (error) {
                console.error('Error updating class:', error);
                alert('An error occurred while updating the class.');
            }
        });
    }

    // Handle deleteModal to fetch classId from data-class-id or editModal
    const deleteModal = document.getElementById('deleteModal');
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function (event) {
            // Get the button that triggered the modal
            const button = event.relatedTarget;
            
            // Check if it's a button with data-class-id attribute
            let classId = button ? button.getAttribute('data-class-id') : null;
            
            // If no data-class-id on button, try to get it from editModal's hidden input
            if (!classId) {
                const editClassIdInput = document.getElementById('editClassId');
                if (editClassIdInput) {
                    classId = editClassIdInput.value;
                }
            }
            
            // Set the classId to deleteClassId input
            const deleteClassIdInput = document.getElementById('deleteClassId');
            if (deleteClassIdInput) {
                deleteClassIdInput.value = classId || '';
            }
        });
    }

    // Handle delete class form submission via AJAX
    const deleteClassForm = document.getElementById('deleteClassForm');
    if (deleteClassForm) {
        deleteClassForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(deleteClassForm);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            try {
                const response = await fetch("", {
                    method: "POST",
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    // Close the delete modal
                    const deleteModalInstance = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
                    if (deleteModalInstance) {
                        deleteModalInstance.hide();
                    }
                    // Close the edit modal if it's open
                    const editModalInstance = bootstrap.Modal.getInstance(document.getElementById('editModal'));
                    if (editModalInstance) {
                        editModalInstance.hide();
                    }
                    // Reload the page to show updated data
                    window.location.reload();
                } else {
                    alert('Error: ' + (data.error || 'Failed to delete class'));
                }
            } catch (error) {
                console.error('Error deleting class:', error);
                alert('An error occurred while deleting the class.');
            }
        });
    }
});
