// Social Intent website – Eleventy configuration
// Content lives in src/. Build output goes to _site/.
export default function (eleventyConfig) {
  // Copy static assets and the CMS admin straight through
  eleventyConfig.addPassthroughCopy({ "src/assets": "assets" });
  eleventyConfig.addPassthroughCopy({ "src/admin": "admin" });
  eleventyConfig.addPassthroughCopy({ "src/_redirects": "_redirects" });

  // Collections: newest first
  const byDateDesc = (a, b) => b.date - a.date;
  eleventyConfig.addCollection("insights", (api) =>
    api.getFilteredByGlob("src/insights/*.md").sort(byDateDesc)
  );
  eleventyConfig.addCollection("work", (api) =>
    api.getFilteredByGlob("src/work/*.md").sort((a, b) => (a.data.order ?? 99) - (b.data.order ?? 99))
  );
  eleventyConfig.addCollection("resources", (api) =>
    api.getFilteredByGlob("src/resources/*.md").sort((a, b) => (a.data.order ?? 99) - (b.data.order ?? 99))
  );

  // Guides that are really on sale (status available and a real Payhip link) get their own page
  eleventyConfig.addCollection("guidesLive", (api) =>
    api.getFilteredByGlob("src/resources/*.md")
      .filter((g) => g.data.status === "available" && g.data.payhip && !g.data.payhip.includes("REPLACE"))
      .sort((a, b) => (a.data.order ?? 99) - (b.data.order ?? 99))
  );

  // Filters
  eleventyConfig.addFilter("readableDate", (d) =>
    new Date(d).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" })
  );
  eleventyConfig.addFilter("isoDate", (d) => new Date(d).toISOString().slice(0, 10));
  eleventyConfig.addFilter("limit", (arr, n) => arr.slice(0, n));
  eleventyConfig.addFilter("where", (arr, key, val) => arr.filter((x) => x.data[key] === val));
  eleventyConfig.addFilter("money", (n) => "£" + Number(n).toFixed(n % 1 ? 2 : 0));

  return {
    dir: { input: "src", output: "_site", includes: "_includes", data: "_data" },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
    templateFormats: ["njk", "md", "html"],
  };
}
