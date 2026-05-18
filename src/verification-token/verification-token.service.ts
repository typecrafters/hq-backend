import { Injectable } from "@nestjs/common";
import { InjectModel } from "@nestjs/mongoose";
import { VerificationToken, type VerificationTokenDocument } from "./verification-token.schema";
import type { Model } from "mongoose";
import { createHash, randomBytes } from "crypto";
import { TokenType } from "./dto/token-type.enum";
import { Duration } from "@/common/class/duration";

@Injectable()
export class VerificationTokenService {
    constructor(
        @InjectModel(VerificationToken.name) private readonly tokenModel: Model<VerificationTokenDocument>
    ) { }

    public hash(token: string): string {
        return createHash("sha256")
            .update(token)
            .digest("hex");
    }

    public async createForEmail(uid: string): Promise<string> {
        return this.create(
            uid,
            TokenType.EmailVerification,
            Duration.ofDays(1).toSeconds()
        );
    }

    public async createForPassword(uid: string): Promise<string> {
        return this.create(
            uid,
            TokenType.PasswordReset,
            Duration.ofHours(1).toSeconds()
        );
    }

    private async create(uid: string, type: TokenType,ttlSeconds: number): Promise<string> {
        const token = randomBytes(32).toString("hex");

        await this.tokenModel.create({
            hash: this.hash(token),
            uid,
            type,
            expiresAt: Duration.ofSeconds(ttlSeconds).fromNow()
        });

        return token;
    }

    public async validateEmailToken(token: string, uid: string): Promise<boolean> {
        return this.validate(
            token,
            uid,
            TokenType.EmailVerification
        );
    }

    public async validatePasswordToken(token: string, uid: string): Promise<boolean> {
        return this.validate(
            token,
            uid,
            TokenType.PasswordReset
        );
    }

    public async consumeEmailToken(token: string, uid: string): Promise<boolean> {
        return this.consume(
            token,
            uid,
            TokenType.EmailVerification
        );
    }

    public async consumePasswordToken(token: string, uid: string): Promise<boolean> {
        return this.consume(
            token,
            uid,
            TokenType.PasswordReset
        );
    }

    private async validate(input: string, uid: string, type: TokenType): Promise<boolean> {
        const hash = this.hash(input);

        const token = await this.tokenModel.findOne({
            hash,
            uid,
            type
        });

        if (!token) {
            return false;
        }

        if (token.expiresAt.getTime() <= Date.now()) {
            await this.tokenModel.deleteOne({ _id: token.id });
            return false;
        }

        return true;
    }

    private async consume(input: string, uid: string, type: TokenType): Promise<boolean> {
        const hash = this.hash(input);

        const token = await this.tokenModel.findOne({
            hash,
            uid,
            type
        });

        if (!token) {
            return false;
        }

        if (token.expiresAt.getTime() <= Date.now()) {
            await this.tokenModel.deleteOne({ _id: token.id });
            return false;
        }

        await this.tokenModel.deleteMany({ uid, type });
        return true;
    }


}
