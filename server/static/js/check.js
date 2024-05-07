function checkLogin() {
  const token = window.sessionStorage.getItem("token");
  if (token === null) {
    return false;
  }

  return token;
}
