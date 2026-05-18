import { BadRequestException, Injectable, UnauthorizedException } from "@nestjs/common";
import { InjectModel } from "@nestjs/mongoose";
import { User, type UserDocument } from "./user.schema";
import type { Model } from "mongoose";
import type { CreateUserRequest } from "./dto/create-user-request.dto";
import { MailService } from "../mail/mail.service";
import type { FileService } from "@/file/file.service";
import { UserStatus } from "./dto/user-status.enum";
import type { ConfigService } from "@nestjs/config";
import type { VerificationTokenService } from "@/verification-token/verification-token.service";
import bcrypt from "bcrypt";

@Injectable()
export class UserService {
    constructor(
        @InjectModel(User.name) private readonly userModel: Model<UserDocument>,
        private readonly config: ConfigService,
        private readonly fileService: FileService,
        private readonly tokenService: VerificationTokenService,
        private readonly mailService: MailService,
    ) { }

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
    }

    public async validateEmail(uid: string, token: string): Promise<boolean> {
        return await this.tokenService.validateEmailToken(token, uid);
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

        user.password = await bcrypt.hash(password, 10);
        user.status = UserStatus.Active;

        await user.save();
        await this.tokenService.consumeEmailToken(token, uid);
        return user;
    }
}