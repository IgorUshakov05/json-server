const jsonServer = require("json-server");
const server = jsonServer.create();
const router = jsonServer.router("db.json");
const middlewares = jsonServer.defaults();

// Middleware для предотвращения дубликатов в to_watch
server.use((req, res, next) => {
  if (
    req.method === "POST" &&
    (req.url === "/to-watch/movies" || req.url === "/to-watch/series")
  ) {
    const title = req.body.title;
    if (!title) {
      return res.status(400).json({ error: "Title is required" });
    }

    // Проверяем, существует ли уже такой элемент в списке
    const db = router.db;
    const collectionName = req.url.split("/")[2]; // movies или series
    const collection = db.get(`to_watch_${collectionName}`);

    const exists = collection.find({ title }).value();
    if (exists) {
      return res
        .status(400)
        .json({ error: "Item already exists in the 'To Watch' list" });
    }

    // Если элемент не найден, добавляем его
    collection.push({ title }).write();
    return res
      .status(201)
      .json({ message: "Item added to 'To Watch' list", title });
  }
  next();
});

// Используем стандартные middleware и роутер
server.use(middlewares);
server.use(router);

// Запускаем сервер
const port = process.env.PORT || 3000;
server.listen(port, () => {
  console.log(`JSON Server is running on port ${port}`);
});
