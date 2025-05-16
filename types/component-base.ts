export interface ComponentBase {
  /**
   * CSS class names to apply to the component
   */
  className?: string;
  
  /**
   * Unique identifier for the component
   */
  id?: string;
  
  /**
   * Test identifier for the component
   */
  testId?: string;
}

export interface Loadable {
  /**
   * Whether the component is in a loading state
   */
  isLoading?: boolean;
  
  /**
   * Text to display when in loading state
   */
  loadingText?: string;
}
