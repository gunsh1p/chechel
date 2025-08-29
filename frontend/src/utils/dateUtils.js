// Utility function to safely format dates
export const formatDate = (dateString) => {
  if (!dateString || dateString === null || dateString === undefined) {
    return 'Unknown'
  }
  
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) {
      return 'Invalid Date'
    }
    return date.toLocaleDateString()
  } catch (error) {
    return 'Invalid Date'
  }
}

// Utility function to safely format date and time
export const formatDateTime = (dateString) => {
  if (!dateString || dateString === null || dateString === undefined) {
    return 'Unknown'
  }
  
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) {
      return 'Invalid Date'
    }
    return date.toLocaleString()
  } catch (error) {
    return 'Invalid Date'
  }
}