/* ==========================================================================
   Maniro — Contact Page / Contact Form validation
   Pure front-end validation (no backend wired yet). Validates on blur and
   on submit, shows inline error messages, keeps aria-invalid / the error
   message in sync for assistive tech, and focuses the first invalid field.
   ========================================================================== */

(function () {
  "use strict";

  var form = document.getElementById("contact-form");
  if (!form) return;

  var status = document.getElementById("contact-form-status");

  var rules = {
    name: {
      test: function (value) {
        return value.trim().length >= 2;
      },
      message: "لطفاً نام خود را کامل وارد کنید (حداقل ۲ حرف).",
    },
    phone: {
      test: function (value) {
        return /^[0-9+\-\s()]{8,15}$/.test(value.trim());
      },
      message: "لطفاً یک شماره تماس معتبر وارد کنید.",
    },
    email: {
      test: function (value) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
      },
      message: "لطفاً یک ایمیل معتبر وارد کنید.",
    },
    subject: {
      test: function (value) {
        return value.trim().length >= 3;
      },
      message: "لطفاً موضوع پیام را وارد کنید.",
    },
    message: {
      test: function (value) {
        return value.trim().length >= 10;
      },
      message: "پیام باید حداقل ۱۰ حرف باشد.",
    },
  };

  var fields = Array.prototype.slice.call(
    form.querySelectorAll("input[name], textarea[name]")
  );

  function validateField(fieldEl) {
    var rule = rules[fieldEl.name];
    if (!rule) return true;

    var wrapper = fieldEl.closest(".form-field");
    var errorEl = wrapper.querySelector(".field-error");
    var valid = rule.test(fieldEl.value);

    wrapper.classList.toggle("is-invalid", !valid);
    wrapper.classList.toggle("is-valid", valid);
    fieldEl.setAttribute("aria-invalid", String(!valid));
    if (errorEl) errorEl.textContent = valid ? "" : rule.message;

    return valid;
  }

  function clearField(fieldEl) {
    var wrapper = fieldEl.closest(".form-field");
    var errorEl = wrapper.querySelector(".field-error");
    wrapper.classList.remove("is-invalid", "is-valid");
    fieldEl.removeAttribute("aria-invalid");
    if (errorEl) errorEl.textContent = "";
  }

  function showStatus(message, type) {
    if (!status) return;
    status.textContent = message;
    status.classList.remove("is-success", "is-error");
    status.classList.add(
      "is-visible",
      type === "success" ? "is-success" : "is-error"
    );
  }

  fields.forEach(function (fieldEl) {
    fieldEl.addEventListener("blur", function () {
      validateField(fieldEl);
    });

    /* Re-validate as the user types, but only once a field has already
       been flagged invalid — avoids nagging the person before they've
       even finished typing their first entry. */
    fieldEl.addEventListener("input", function () {
      var wrapper = fieldEl.closest(".form-field");
      if (wrapper.classList.contains("is-invalid")) {
        validateField(fieldEl);
      }
    });
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    var firstInvalid = null;
    var allValid = fields.reduce(function (acc, fieldEl) {
      var valid = validateField(fieldEl);
      if (!valid && !firstInvalid) firstInvalid = fieldEl;
      return acc && valid;
    }, true);

    if (!allValid) {
      if (firstInvalid) firstInvalid.focus();
      showStatus("لطفاً خطاهای فرم را برطرف کنید.", "error");
      return;
    }

    /* No backend connected yet — placeholder success feedback only. */
    showStatus(
      "پیام شما با موفقیت ثبت شد (نمونه — بدون اتصال به بک‌اند).",
      "success"
    );
    form.reset();
    fields.forEach(clearField);
    if (fields[0]) fields[0].focus();
  });
})();
