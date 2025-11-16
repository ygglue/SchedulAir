document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('addSubjectForm');
    const message = document.getElementById('formMessage');

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
});