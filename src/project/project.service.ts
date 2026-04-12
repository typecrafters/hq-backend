import { Injectable, InternalServerErrorException, NotFoundException } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Project } from "./project.entity";
import { MongoRepository } from "typeorm";
import { CreateProjectRequest } from "./dto/create-project-request.dto";
import { UpdateProjectRequest } from "./dto/update-project-request.dto";
import { ObjectId } from "mongodb";
import { FileService } from "@/file/file.service";

@Injectable()
export class ProjectService {
    constructor(
        @InjectRepository(Project) private readonly projectRepository: MongoRepository<Project>,
        private readonly fileService: FileService
    ) { }

    public async list(page: number, limit: number): Promise<Array<Project>> {
        const maxLimit = 24;
        const clamp = Math.min(limit, maxLimit);
        try {
            const projects = await this.projectRepository.find({
                skip: clamp * (page - 1),
                take: clamp,
                order: { createdAt: -1 }
            });

            return await Promise.all(projects.map(async p => {
                p.thumbnailUrl = await this.fileService.getSignedUrl(p.thumbnailUrl);
                return p;
            }));
        } catch {
            throw new InternalServerErrorException("Failed to fetch project list.");
        }
    }

    public async get(id: string): Promise<Project> {
        const notFound = new NotFoundException("Project '" + id + "' not found.");
        if (!ObjectId.isValid(id)) throw notFound;

        const project = await this.projectRepository.findOneBy({ _id: new ObjectId(id) });
        if (project == null) throw notFound;

        project.thumbnailUrl = await this.fileService.getSignedUrl(project.thumbnailUrl);
        return project;
    }

    public async create(request: CreateProjectRequest, userId: string): Promise<Project> {
        const project: Project = this.projectRepository.create({
            ...request,
            thumbnailUrl: request.thumbnailUrl ?? this.fileService.placeholder,
            content: request.content ?? "",
            tags: request.tags ?? [],
            createdBy: userId
        });

        return await this.projectRepository.save(project);
    }

    public async update(id: string, request: UpdateProjectRequest): Promise<void> {
        const notFound = new NotFoundException("Project '" + id + "' not found.");
        if (!ObjectId.isValid(id)) throw notFound;

        const patch = Object.fromEntries(
            Object.entries(request).filter(([_, v]) => v != null)
        );

        if (Object.keys(patch).length === 0) return;

        try {
            const result = await this.projectRepository.updateOne(
                { _id: new ObjectId(id) },
                { $set: patch }
            );

            if (result.matchedCount === 0) throw notFound;
        } catch {
            throw new InternalServerErrorException("Failed to update project.");
        }
    }

    public async delete(id: string): Promise<void> {
        const notFound = new NotFoundException("Project '" + id + "' not found.");
        if (!ObjectId.isValid(id)) throw notFound;

        try {
            const result = await this.projectRepository.deleteOne({ _id: new ObjectId(id) });
            if (result.deletedCount === 0) throw notFound;
        } catch {
            throw new InternalServerErrorException("Failed to delete project.");
        }
    }
}