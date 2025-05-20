import { useState, useRef } from "react";

export function useForm({
  initialValues,
  onSubmit,
  validate,
  validateOnBlur,
  onChange,
}: any) {
  const [values, setValues] = useState(initialValues);
  const [touched, setTouched] = useState<any>({});
  const [errors, setErrors] = useState<any>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Validação
  const runValidation = (vals = values) => {
    if (validate) {
      const errs = validate(vals);
      setErrors(errs || {});
      return errs;
    }
    setErrors({});
    return {};
  };

  // handleChange: (chave, valor) OU evento
  const handleChange = (keyOrEvent: any, value?: any) => {
    if (typeof keyOrEvent === "string") {
      setValues((prev: any) => {
        const next = { ...prev, [keyOrEvent]: value };
        if (onChange) onChange(next);
        if (validateOnBlur) runValidation(next);
        return next;
      });
    } else if (keyOrEvent && keyOrEvent.target) {
      const { name, value: v } = keyOrEvent.target;
      setValues((prev: any) => {
        const next = { ...prev, [name]: v };
        if (onChange) onChange(next);
        if (validateOnBlur) runValidation(next);
        return next;
      });
    }
  };

  // handleBlur: marca como tocado e valida se necessário
  const handleBlur = (key: string) => {
    setTouched((prev: any) => ({ ...prev, [key]: true }));
    if (validateOnBlur) runValidation();
  };

  // reset: volta ao estado inicial
  const reset = () => {
    setValues(initialValues);
    setTouched({});
    setErrors({});
  };

  // handleSubmit: submit do form
  const handleSubmit = async (e?: any) => {
    if (e && e.preventDefault) e.preventDefault();
    setTouched(
      Object.keys(values).reduce((acc, k) => ({ ...acc, [k]: true }), {})
    );
    const errs = runValidation();
    if (errs && Object.keys(errs).length > 0) return;
    setIsSubmitting(true);
    try {
      await onSubmit(values);
    } finally {
      setIsSubmitting(false);
    }
  };

  // isValid: sem erros
  const isValid = Object.keys(errors).length === 0;

  return {
    values,
    setValues,
    handleChange,
    handleBlur,
    touched,
    errors,
    isSubmitting,
    isValid,
    reset,
    handleSubmit,
  };
}
