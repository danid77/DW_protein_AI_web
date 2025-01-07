export  function adjustInputField(selectElement) {
    const inputField = selectElement.closest(".entity-card").querySelector(".input-sequence");
    if (selectElement.value === "Protein") {
        const textarea = document.createElement("textarea");
        textarea.className = "form-control input-sequence";
        textarea.rows = 3;
        textarea.placeholder = "Paste Sequence or FASTA";
        inputField.replaceWith(textarea);
    } else {
        const input = document.createElement("input");
        input.type = "text";
        input.className = "form-control input-sequence";
        input.placeholder = "Input";
        inputField.replaceWith(input);
    }
}