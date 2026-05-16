/// <reference types="node" />

import { NestFactory } from "@nestjs/core";
import { ValidationPipe } from "@nestjs/common";
import { AppModule } from "./app.module";
import { ConfigService } from "@nestjs/config";
import { type NestExpressApplication } from "@nestjs/platform-express";
import cookieParser from "cookie-parser";

(async () => {
    const app = await NestFactory.create<NestExpressApplication>(AppModule);

    app.setGlobalPrefix("api");
    app.useGlobalPipes(new ValidationPipe({ transform: true }));
    app.use(cookieParser());
    app.set("trust proxy", true);
    
    const config = app.get(ConfigService);
    
    app.enableCors({
        origin: config.getOrThrow<string>("ALLOWED_ORIGINS").split(",").map(o => o.trim()),
        methods: "*",
        allowedHeaders: "*",
        credentials: true
    });

    const host = config.getOrThrow("APP_HOST");
    const port = config.getOrThrow("APP_PORT");

    await app.listen(port, host, () => console.log("App is listening at http://%s:%s/", host, port));
})();