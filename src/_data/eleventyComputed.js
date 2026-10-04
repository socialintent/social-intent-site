// Gives every page a `root` prefix ("" at the top level, "../" one folder down)
// so links and assets work wherever the site is hosted, including sub-paths.
export default {
  root: (data) => {
    const url = data.page && data.page.url ? data.page.url : "/";
    const depth = url.split("/").filter(Boolean).length - 1;
    return depth > 0 ? "../".repeat(depth) : "";
  },
};
