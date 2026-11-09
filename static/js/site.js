document.addEventListener('DOMContentLoaded', () => {
  const money = (amount) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount);

  document.querySelectorAll('.qty-step').forEach((button) => {
    button.addEventListener('click', () => {
      const input = button.parentElement.querySelector('input[type="number"]');
      if (!input) return;
      const min = Number(input.min || 1);
      const max = Number(input.max || 9999);
      const current = Number(input.value || min);
      input.value = String(Math.min(max, Math.max(min, current + Number(button.dataset.step || 0))));
      input.dispatchEvent(new Event('change', { bubbles: true }));
    });
  });

  const cartSummary = document.querySelector('[data-cart-summary]');
  if (cartSummary) {
    const updateTotals = () => {
      let subtotal = 0;
      document.querySelectorAll('.cart-line').forEach((line) => {
        const unitPrice = Number(line.dataset.unitPrice || 0);
        const quantity = Number(line.querySelector('.cart-quantity')?.value || 0);
        const lineTotal = unitPrice * Math.max(0, quantity);
        subtotal += lineTotal;
        const lineLabel = line.querySelector('.line-total');
        if (lineLabel) lineLabel.textContent = money(lineTotal);
      });
      subtotal = Math.round((subtotal + Number.EPSILON) * 100) / 100;
      const tax = Math.round((subtotal * Number(cartSummary.dataset.taxRate || 0.10) + Number.EPSILON) * 100) / 100;
      const subtotalLabel = cartSummary.querySelector('[data-subtotal]');
      const taxLabel = cartSummary.querySelector('[data-tax]');
      const totalLabel = cartSummary.querySelector('[data-total]');
      if (subtotalLabel) subtotalLabel.textContent = money(subtotal);
      if (taxLabel) taxLabel.textContent = money(tax);
      if (totalLabel) totalLabel.textContent = money(subtotal + tax);
    };
    document.querySelectorAll('.cart-quantity').forEach((input) => input.addEventListener('input', updateTotals));
  }

  document.querySelectorAll('.toast-close').forEach((button) => {
    button.addEventListener('click', () => button.closest('.toast')?.remove());
  });
  document.querySelectorAll('.toast').forEach((toast) => {
    window.setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-5px)';
      window.setTimeout(() => toast.remove(), 200);
    }, 5200);
  });

  document.querySelectorAll('[data-password-match]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      const password = form.querySelector('input[name="password1"]');
      const confirmation = form.querySelector('input[name="password2"]');
      const error = form.querySelector('[data-password-error]');
      if (!password || !confirmation || !error) return;
      if (password.value !== confirmation.value) {
        event.preventDefault();
        error.hidden = false;
        confirmation.setAttribute('aria-invalid', 'true');
        confirmation.focus();
      } else {
        error.hidden = true;
        confirmation.removeAttribute('aria-invalid');
      }
    });
  });

  document.querySelectorAll('[data-client-validate]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      const invalid = [...form.querySelectorAll('input[required], select[required]')].find((field) => !field.checkValidity());
      if (invalid) {
        event.preventDefault();
        invalid.reportValidity();
      }
    });
  });
});
