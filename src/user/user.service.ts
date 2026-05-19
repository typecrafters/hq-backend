import { BadRequestException, Injectable, UnauthorizedException } from "@nestjs/common";
import { InjectModel } from "@nestjs/mongoose";
import { User, type UserDocument } from "./user.schema";
import type { Model } from "mongoose";
import type { CreateUserRequest } from "./dto/create-user-request.dto";
import { MailService } from "../mail/mail.service";
import { FileService } from "@/file/file.service";
import { UserStatus } from "./dto/user-status.enum";
import { ConfigService } from "@nestjs/config";
import { VerificationTokenService } from "@/verification-token/verification-token.service";
import bcrypt from "bcrypt";
import { Optional } from "@/common/class/optional";

@Injectable()
export class UserService {
    constructor(
        @InjectModel(User.name) private readonly userModel: Model<UserDocument>,
        private readonly config: ConfigService,
        private readonly fileService: FileService,
        private readonly tokenService: VerificationTokenService,
        private readonly mailService: MailService,
    ) { }

    private async hashPassword(password: string) {
        return await bcrypt.hash(password, 10);
    }

    public async list(page: number, limit: number): Promise<[Array<User>, number, number, number]> {
        const safePage = Number.isFinite(page) && page > 0 ? Math.floor(page) : 1;
        const safeLimit = Number.isFinite(limit) ? Math.floor(limit) : 10;
        const clampedLimit = Math.min(100, Math.max(1, safeLimit));
        const skip = (safePage - 1) * clampedLimit;

        const [result, total] = await Promise.all([
            this.userModel.find().skip(skip).limit(clampedLimit).exec(),
            this.userModel.countDocuments().exec(),
        ]);

        const users = await Promise.all(result.map(async u => {
            u.profilePictureUrl = await this.fileService.getSignedUrl(u.profilePictureUrl);
            return u;
        }));

        return [users, skip, clampedLimit, total];
    }

    public async get(id: string): Promise<Optional<User>> {
        return Optional.ofNullable(await this.userModel.findById(id).exec());
    }

    public async create(request: CreateUserRequest) {
        const user = await this.userModel.create({
            firstName: request.firstName,
            lastName: request.lastName,
            email: request.email,
            role: request.role,
            password: null,
            profilePictureUrl: this.fileService.placeholder,
            status: UserStatus.Unverified,
            permissions: request.permissions,
        });

        const uid = user._id.toString();
        const token = await this.tokenService.createForEmail(uid);
        const url = new URL("/hq/users/email/verify", this.config.getOrThrow<string>("PAGE_URL"));
        url.searchParams.set("uid", uid);
        url.searchParams.set("token", token);

        await this.mailService.renderAndSend(request.email, "Verify your email address.", "verify-email.ejs", {
            url,
            firstName: request.firstName
        });

        return user._id.toString();
    }

    public async validateEmail(uid: string, token: string): Promise<boolean> {
        return await this.tokenService.validateEmailToken(token, uid);
    }

    public async requestPasswordReset(email: string) {
        const user = await this.userModel.findOne({ email });
        if (!user || !user.password) return;

        const uid = user._id.toString();
        const token = await this.tokenService.createForPassword(uid);
        const url = new URL("/hq/users/password/reset", this.config.getOrThrow<string>("PAGE_URL"));
        url.searchParams.set("uid", uid);
        url.searchParams.set("token", token);

        await this.mailService.renderAndSend(email, "Reset your password", "password-reset.ejs", {
            url,
            firstName: user.firstName,
        });
    }

    public async activateUserAccount(uid: string, token: string, password: string, confirmPassword: string) {
        const unauthorized = new UnauthorizedException("Unauthorized.");
        
        if (!(await this.tokenService.validateEmailToken(token, uid))) {
            throw unauthorized
        }

        if (password !== confirmPassword) {
            throw new BadRequestException("Passwords do not match");
        }
        const user = await this.userModel.findById(uid);

        if (!user) {
            throw unauthorized
        }

        if (user.password) {
            throw unauthorized;
        }

        user.password = await this.hashPassword(password);
        user.status = UserStatus.Active;

        await user.save();
        await this.tokenService.consumeEmailToken(token, uid);
        return user;
    }

    public async resetPassword(uid: string, token: string, password: string, confirmPassword: string) {
        const unauthorized = new UnauthorizedException("Unauthorized.");

        if (!(await this.tokenService.validatePasswordToken(token, uid))) {
            throw unauthorized;
        }

        if (password !== confirmPassword) {
            throw new BadRequestException("Passwords do not match");
        }

        const user = await this.userModel.findById(uid);
        if (!user) throw unauthorized;

        user.password = await bcrypt.hash(password, 10);

        await user.save();
        await this.tokenService.consumePasswordToken(token, uid);
        return user;
    }
}